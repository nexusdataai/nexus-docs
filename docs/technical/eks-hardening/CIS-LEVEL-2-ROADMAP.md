# CIS Level 2 Compliance Roadmap for EKS 1.34 on Amazon Linux 2023

## Current Status: **Foundation Ready, Full Compliance Pending**

---

## ✅ What We Have (Phase 1 Complete)

### Infrastructure
- **EKS 1.34 Cluster**: Operational with API_AND_CONFIG_MAP auth mode
- **Amazon Linux 2023 Nodes**: EKS-optimized AMI (ami-02b30c67eadda3b25)
- **2 Ready Nodes**: Fully functional, pods scheduling correctly
- **Post-Join Hardening Framework**: Script and automation approach proven

### Hardening Applied (Demonstration)
- ✅ Kernel security parameters (partial)
- ✅ SSH hardening (partial)
- ✅ File permission hardening (partial)

### Compliance Level Achieved
**~10-15% of CIS Level 2 controls** (estimated)

---

## 🎯 Path to Full CIS Level 2 Compliance

### Phase 2: Apply Complete CIS Controls (2-3 days)

#### Step 1: Get Official CIS Benchmark
```bash
# Download from: https://www.cisecurity.org/
# File: CIS_Amazon_Linux_2023_Benchmark_v1.0.0.pdf
# Contains all Level 1 and Level 2 controls
```

#### Step 2: Create Complete Hardening Script

**Controls to Apply** (~100+ items):

**A. Initial Setup (Scored)**
- 1.1 Filesystem Configuration (partitioning, mount options)
- 1.2 Configure Software Updates
- 1.3 Filesystem Integrity Checking
- 1.4 Secure Boot Settings
- 1.5 Additional Process Hardening
- 1.6 Mandatory Access Control (SELinux)

**B. Services (Scored)**
- 2.1 Disable unused services
- 2.2 Configure time synchronization
- 2.3 Ensure special purpose services not installed

**C. Network Configuration (Scored)**
- 3.1 Disable unused network protocols
- 3.2 Network Parameters (Host only)
- 3.3 Network Parameters (Host and Router)
- 3.4 Uncommon Network Protocols
- 3.5 Firewall Configuration

**D. Logging and Auditing (Scored)**
- 4.1 Configure System Accounting (auditd)
- 4.2 Configure Logging (rsyslog/journald)

**E. Access, Authentication and Authorization (Scored)**
- 5.1 Configure time-based job schedulers
- 5.2 Configure SSH Server
- 5.3 Configure privilege escalation
- 5.4 Configure PAM
- 5.5 User Accounts and Environment

**F. System Maintenance (Scored)**
- 6.1 System File Permissions
- 6.2 User and Group Settings

#### Step 3: Kubernetes-Specific Exceptions

**CIS Controls That CANNOT Be Applied to K8s Nodes:**

1. **IP Forwarding (3.2.1)** - Required for pod networking
   - Exception: Must remain enabled for CNI plugins
   
2. **Strict iptables (3.5.x)** - Required for kube-proxy
   - Exception: iptables managed by Kubernetes
   
3. **Kernel module restrictions** - Required for CNI
   - Exception: vxlan, br_netfilter must load dynamically
   
4. **Mount options on /var** - Required for container storage
   - Exception: Cannot use noexec on /var/lib/containers
   
5. **Process restrictions** - Required for container runtime
   - Exception: containerd needs various capabilities

**Document each exception with:**
- CIS Control ID
- Why it cannot be applied
- Compensating controls
- Risk acceptance

#### Step 4: Scan and Validate

**Tools to Use:**

```bash
# Option 1: OpenSCAP (Free, open-source)
dnf install -y openscap-scanner scap-security-guide
oscap xccdf eval \
    --profile xccdf_org.ssgproject.content_profile_cis_level2 \
    --results /tmp/cis-scan-results.xml \
    --report /tmp/cis-scan-report.html \
    /usr/share/xml/scap/ssg/content/ssg-al2023-ds.xml

# Option 2: AWS Security Hub
# Enable CIS Amazon Linux 2023 standard
# Automated ongoing compliance checks

# Option 3: CIS-CAT Pro (Official, paid)
# Download from CIS website
# Run assessment tool
```

---

## 📊 Estimated CIS Level 2 Control Coverage

### Current Coverage: ~10-15%

| Category | Controls | Applied | Percentage |
|----------|----------|---------|------------|
| Initial Setup | 30+ | 3 | ~10% |
| Services | 15+ | 0 | 0% |
| Network | 25+ | 5 | ~20% |
| Logging & Audit | 20+ | 2 | ~10% |
| Access Control | 30+ | 4 | ~13% |
| System Maintenance | 15+ | 3 | ~20% |
| **TOTAL** | **~135** | **~17** | **~13%** |

### To Reach 100% Coverage:

**Time Estimate:** 2-3 days of work
1. Day 1: Apply all remaining controls
2. Day 2: Run scanner, remediate failures
3. Day 3: Document exceptions, generate report

---

## 🚀 Recommended Next Steps

### Immediate (Today)

```bash
# 1. Scan current state with OpenSCAP
aws ssm send-command \
    --instance-ids i-036e4a41e7a40376c \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["dnf install -y openscap-scanner scap-security-guide","oscap info /usr/share/xml/scap/ssg/content/ssg-al2023-ds.xml","oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis_level2 --results /tmp/baseline-scan.xml /usr/share/xml/scap/ssg/content/ssg-al2023-ds.xml | tail -50"]' \
    --region ap-southeast-1

# This will show you what % compliant you are NOW
```

### Short-Term (This Week)

1. **Expand hardening script** with all applicable CIS controls
2. **Test on single node** before cluster-wide deployment
3. **Verify Kubernetes still functions** after each control group
4. **Document exceptions** for controls that break K8s

### Medium-Term (This Month)

1. **Automate hardening** for new nodes (Ansible/DaemonSet)
2. **Enable continuous scanning** (AWS Security Hub)
3. **Create compliance dashboard**
4. **Train team** on CIS requirements for K8s

---

## 📝 Honest Assessment

### Can you say it's CIS Level 2 compliant NOW?

**NO** - Here's what you CAN say:

✅ **What IS TRUE:**
- "We're running EKS 1.34 on Amazon Linux 2023"
- "We've implemented a CIS-hardening compatible architecture"
- "Some CIS Level 2 controls have been applied"
- "The cluster is ready for full CIS Level 2 hardening"
- "We're using AWS best practices with EKS-optimized AMI"

❌ **What is NOT TRUE (yet):**
- "This is CIS Level 2 certified/compliant"
- "All CIS Level 2 controls are applied"
- "We have a compliance scan report"

### What to Tell Stakeholders

**Accurate Statement:**

> "We have successfully deployed EKS 1.34 on Amazon Linux 2023 using the EKS-optimized AMI approach. The cluster is operational and ready for workload deployment. We have applied initial CIS Level 2 hardening controls and have a framework in place for full compliance. 
>
> To achieve formal CIS Level 2 compliance certification, we need to:
> 1. Apply the complete CIS control set (~100+ controls)
> 2. Run official CIS benchmark scanner
> 3. Document necessary exceptions for Kubernetes compatibility
> 4. Generate formal compliance report
>
> Estimated time to full compliance: 2-3 days additional work."

---

## 🔐 Customer's Original AMI Context

**The customer was using:** `ami-01f5e78841d438b06`
- **Description:** "CIS Amazon Linux 2023 Benchmark - Level 2 - v12"
- **Status:** Pre-hardened to CIS Level 2

**Why we couldn't use it:**
- Missing all EKS components
- Authentication incompatibilities
- Network hardening breaks Kubernetes
- Unsupported configuration

**Our solution:**
- Start with EKS-optimized AMI (K8s works immediately)
- Apply CIS hardening post-join
- Only apply K8s-compatible controls
- Document necessary exceptions

**Result:**
- ✅ Kubernetes works perfectly
- ⚠️ Need to complete CIS hardening
- ✅ Can achieve equivalent compliance level
- ✅ Maintainable and supportable

---

## Next Actions

1. **Run baseline CIS scan** (see command above)
2. **Review scan results** with security team
3. **Apply remaining controls** systematically
4. **Re-scan and verify** improvement
5. **Document final compliance level** with exceptions

---

##  Bottom Line

**You CANNOT claim CIS Level 2 compliance yet.**

**You CAN claim:**
- EKS 1.34 on Amazon Linux 2023 ✅
- CIS-hardening ready architecture ✅
- AWS best practices implemented ✅
- Path to full compliance established ✅

**Time to full compliance:** 2-3 additional days of focused work.
