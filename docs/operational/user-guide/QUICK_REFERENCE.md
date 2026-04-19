# Quick Reference Card

## Deployment Wizard Steps

| Step | Action | Time |
|------|--------|------|
| 1 | Select Capability | 1 min |
| 2 | Choose Architecture | 1 min |
| 3 | Configure Environment | 2 min |
| 4 | Enter AWS Credentials | 2 min |
| 5 | Verify Permissions | 2 min |
| 6 | Select Strategy | 1 min |
| 7 | Execute Deployment | 15-30 min |
| 8 | Verify Health | 2 min |
| 9 | View Results | - |

## Authentication Methods

| Method | Best For |
|--------|----------|
| **IAM Role ARN** | Cross-account, production |
| **Access Keys** | Quick setup, development |
| **AWS Profile** | Existing CLI users |
| **ADFS/SAML** | Enterprise SSO |

## Deployment Strategies

| Strategy | When to Use |
|----------|-------------|
| **Update Existing** | Healthy stacks |
| **Clean Deploy** | Failed stacks |

## Environment Types

| Environment | Purpose |
|-------------|---------|
| **dev** | Development, testing |
| **staging** | Pre-production |
| **prod** | Production |

## Common Actions

### Install New Capability
```
Get Started → Select Capability → Install → Configure → Deploy
```

### Update Existing
```
Capability Selection → Installed → Update → Configure → Deploy
```

### Delete Deployment
```
Capability Selection → Installed → Delete → Confirm → Execute
```

## Key URLs After Deployment

| Resource | URL Pattern |
|----------|-------------|
| Frontend | `https://app.yourdomain.com` |
| Backend API | `https://api.yourdomain.com` |
| Health Check | `https://api.yourdomain.com/health` |

## First Login

1. Open Frontend URL
2. Username: `admin@capability-name.local`
3. Password: (shown in Results)
4. **Change password on first login!**

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Can't load capabilities | Restart app |
| Access denied | Check IAM policy |
| Deployment stuck | Check CloudFormation |
| 502 error | Check ECS health |
| DNS not working | Wait 15 min |

## Support

- **Docs**: This user guide
- **Email**: support@totogi.com
- **Portal**: support.totogi.com

## Keyboard Shortcuts

| Action | Windows | Mac |
|--------|---------|-----|
| Refresh | F5 | ⌘R |
| Dev Tools | F12 | ⌘⌥I |
| Quit | Alt+F4 | ⌘Q |

---

*Totogi Capability Installer v1.0.0*
