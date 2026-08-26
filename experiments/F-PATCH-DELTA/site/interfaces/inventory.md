# Integration inventory

**Fairbank Donor Network · IT · current as of 2025-11-14**

*FICTIONAL — see [`../README.md`](../README.md).*

---

## Donor hospitals

| Hospital | EHR | Version | Referral channel | Notes |
|---|---|---|---|---|
| H-1102 | Epic | Aug 2024 IU | interfaced, HL7 v2.5.1 ADT | highest volume; also our only evening OR block |
| H-1207 | Epic | Nov 2023 IU | interfaced, HL7 v2.5.1 ADT | different version to H-1102 |
| H-1355 | Meditech | Expanse 2.2 | telephone | no interface, and no plans for one |
| H-1490 | Cerner | 2022.09 | telephone | low volume — four referrals last year |

**Note:** H-1102 and H-1207 are both Epic but at different upgrade levels. The ADT feeds are not identical
and the mapping differs between them.

## Laboratory

| System | Interface | Notes |
|---|---|---|
| Fairbank Reference Laboratory | HL7 v2.5.1 ORU^R01 over MLLP | inbound only; results land in the clinical inbox |

## Imaging

Imaging is **not interfaced.** Studies are obtained by requesting a disc or a share link from the donor
hospital's PACS, case by case. There is no standing arrangement with any hospital.

## E-signature

**DocuSign** — used for authorization capture. The signed artifact is downloaded and attached to the donor
record manually.

## Allocation

UNet access via individual named accounts. **No service account, and no federation with our identity
provider.** Access is provisioned by the Director of Clinical Operations and reviewed annually.

## Identity

Microsoft Entra ID. Single sign-on for internal systems only.
