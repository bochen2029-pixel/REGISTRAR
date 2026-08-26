// REGISTRAR · floor · the batched temporal closure
// ─────────────────────────────────────────────────────────────────────────────
// All-pairs shortest paths in the (min, +) tropical semiring, batched — one
// donor case per block-z. This is `floor/closure.py`'s inner loop, moved to a
// card, for the one question that needs it.
//
// WHAT THIS IS FOR, AND WHAT IT IS NOT
//
//   It is NOT needed for one case. A donor case has a few dozen time points and
//   a lifecycle that is nearly series-parallel, so its induced width is small
//   and the reference closure runs in microseconds on a CPU. The general
//   algorithm is cubic; the domain's structure is what makes it cheap. Claiming
//   a GPU is required for a single case would be a lie.
//
//   It IS for the portfolio counterfactual sweep — the question a supervisor
//   actually has at three in the morning:
//
//       "I have one perfusionist and three cases. If I push this OR by ninety
//        minutes, what breaks, and where does the hour buy the most?"
//
//   That is N live cases × K candidate interventions = tens of thousands of
//   small independent networks. Arithmetic that is GEMM-shaped with (+, ×)
//   replaced by (min, +). It turns a batch job into a question you can answer
//   while the person who asked it is still on the phone.
//
// THE CORRECTNESS ARGUMENT IS THE SEMIRING
//
//   Times are whole minutes. min and + over int32 are EXACTLY associative —
//   there is no floating point anywhere and no accumulated drift. INF is
//   0x3f3f3f3f precisely because INF + INF does not overflow int32.
//
//   So this kernel and the reference implementation must produce BIT-IDENTICAL
//   output, asserted by equality and never by tolerance. That is not a nicety:
//   it is what makes an accelerated path admissible at all under a conformance
//   battery containing replay determinism and floor-with-learned-zeroed. A
//   float implementation would be quicker to write and would silently fail both.
//
//   Concretely, the property this file must satisfy:
//
//       closure_gpu(D) == closure_cpu(D)      for every fixture, exactly
//
//   `floor/parity.py` is the harness that asserts it. Run it on a machine with
//   a card; it is the receipt this kernel does not otherwise have.
//
// STATUS  [SPEC — COMPILED AND PARITY-CHECKED NOWHERE YET]
//
//   No GPU exists in this project's reference environment, so this kernel has
//   never been compiled or executed here. It is published because the argument
//   above is public and the code should be inspectable alongside it — but it
//   carries no measured claim, and `floor/parity.py` will report
//   PASS-UNVERIFIED rather than GREEN until somebody runs it on real hardware.
//
//   If you have a card: compile it, run the parity harness, and send the
//   result. A refutation is as welcome as a confirmation and more useful.
//
//   nvcc -O3 -arch=sm_70 -shared -Xcompiler -fPIC floor/tropical.cu -o floor/libtropical.so
//   nvcc -O3 -arch=sm_70 -o floor/tropical_selftest floor/tropical.cu -DSELFTEST

#include <stdint.h>

#ifndef TILE
#define TILE 16
#endif

#define TROPICAL_INF 0x3f3f3f3f

// ─────────────────────────────────────────────────────────────────────────────
// C = A ⊗ B in the tropical semiring. One case per blockIdx.z.
//
//   ⊕ = min      ⊗ = +
//
// Shared-memory tiling is the ordinary GEMM structure; only the inner
// accumulate changes, from fma to min-of-sum.
// ─────────────────────────────────────────────────────────────────────────────
extern "C" __global__ void tropical_mm(const int32_t* __restrict__ A,
                                       const int32_t* __restrict__ B,
                                       int32_t* __restrict__ C,
                                       int n)
{
    __shared__ int32_t As[TILE][TILE];
    __shared__ int32_t Bs[TILE][TILE];

    const int          b   = blockIdx.z;
    const int          row = blockIdx.y * TILE + threadIdx.y;
    const int          col = blockIdx.x * TILE + threadIdx.x;
    const size_t       off = (size_t)b * (size_t)n * (size_t)n;

    int32_t acc = TROPICAL_INF;

    for (int t = 0; t < n; t += TILE) {
        const int ax = t + threadIdx.x;
        const int by = t + threadIdx.y;

        As[threadIdx.y][threadIdx.x] =
            (row < n && ax  < n) ? A[off + (size_t)row * n + ax ] : TROPICAL_INF;
        Bs[threadIdx.y][threadIdx.x] =
            (by  < n && col < n) ? B[off + (size_t)by  * n + col] : TROPICAL_INF;

        __syncthreads();

        #pragma unroll
        for (int k = 0; k < TILE; ++k) {
            const int32_t a = As[threadIdx.y][k];
            const int32_t c = Bs[k][threadIdx.x];
            // Guard the addition rather than relying on the sentinel absorbing:
            // INF + INF is representable here, but INF + a large finite value
            // is not guaranteed to stay above every finite path in a network
            // with adversarial weights. Explicit is exact.
            if (a < TROPICAL_INF && c < TROPICAL_INF) {
                const int32_t s = a + c;
                if (s < acc) acc = s;
            }
        }
        __syncthreads();
    }

    if (row < n && col < n) {
        C[off + (size_t)row * n + col] = acc;
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// One squaring step: D ← D ⊗ D. Repeated ⌈log₂ n⌉ times, this is the closure.
//
// Repeated squaring rather than Floyd-Warshall because the batch dimension is
// what we are exploiting: FW's k-loop is sequential and serialises the whole
// batch, while squaring is a sequence of independent batched matmuls.
// ─────────────────────────────────────────────────────────────────────────────
extern "C" __global__ void tropical_diag_zero(int32_t* __restrict__ D, int n)
{
    const int b = blockIdx.z;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) {
        D[(size_t)b * n * n + (size_t)i * n + i] = 0;
    }
}

// Negative diagonal after closure ⇒ a negative cycle ⇒ the case is infeasible.
// One flag per case; the host reads it to decide which networks to explain.
extern "C" __global__ void tropical_detect_negative(const int32_t* __restrict__ D,
                                                    int32_t* __restrict__ flags,
                                                    int n)
{
    const int b = blockIdx.z;
    const int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n && D[(size_t)b * n * n + (size_t)i * n + i] < 0) {
        flags[b] = 1;
    }
}

#ifdef SELFTEST
// A standalone check that the semiring arithmetic is what this file claims.
// It does not need a network, a fixture, or the repository — just a card.
#include <stdio.h>

int main(void)
{
    // INF + INF must not overflow int32. This is the whole reason for the
    // choice of sentinel, and it is one line to verify.
    const int64_t doubled = (int64_t)TROPICAL_INF + (int64_t)TROPICAL_INF;
    printf("INF          = %d\n", TROPICAL_INF);
    printf("INF + INF    = %lld  (int32 max = %d)\n",
           (long long)doubled, 2147483647);
    printf("no overflow  : %s\n", doubled < 2147483647 ? "yes" : "NO — SENTINEL IS WRONG");

    int dev = 0;
    cudaError_t e = cudaGetDevice(&dev);
    printf("cuda device  : %s\n", e == cudaSuccess ? "present" : cudaGetErrorString(e));
    return doubled < 2147483647 ? 0 : 1;
}
#endif
