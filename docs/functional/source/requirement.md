# Requirements Document

## Introduction

The Totogi Customer Toolkit is an enterprise-grade management platform that enables customers to deploy modular business capabilities into their own cloud infrastructure (AWS/Azure/GCP/On-premise). The system provides a guided, license-controlled deployment experience with comprehensive operational tooling for monitoring, updates, and lifecycle management. The toolkit supports both Progressive Web Application (PWA) and Electron desktop application delivery models, with multi-factor authentication, role-based access control, and per-capability license validation.

## Glossary

- **Toolkit**: The Totogi Customer Toolkit application (PWA and Electron desktop app)
- **Capability**: A modular business function that can be deployed independently
- **License Key**: A cryptographic token that validates entitlement to deploy specific capabilities
- **Deployment**: The process of provisioning a capability into customer infrastructure
- **Environment**: An isolated deployment target (development, staging, production)
- **Administrator**: User role with full system access and configuration privileges
- **Operator**: User role with limited deployment and monitoring privileges
- **Viewer**: User role with read-only access to dashboards and reports
- **MFA**: Multi-Factor Authentication using TOTP, SMS, or email verification
- **JWT**: JSON Web Token used for session management
- **CloudFormation**: AWS infrastructure-as-code service for provisioning resources
- **Tenant**: An organization or customer entity using the toolkit
- **Entitlement**: The set of capabilities a license key unlocks for deployment
- **Service Worker**: Browser technology enabling offline PWA functionality
- **Electron**: Framework for building cross-platform desktop applications from web technologies
- **Landing Zone**: The foundational infrastructure layer that provides networking, security, and governance for capability deployments
- **Product Enclave**: An isolated deployment environment within a landing zone that hosts one or more capabilities
- **Capability Catalog**: A collection of available business capabilities that can be deployed into product enclaves
- **Drag-and-Drop Deployment**: A visual interface mechanism for deploying capabilities by dragging from the catalog and dropping into a product enclave

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate with username and password, so that I can securely access the toolkit

#### Acceptance Criteria

1. WHEN a user submits valid credentials THEN the Toolkit SHALL authenticate the user and create a session
2. WHEN a user submits invalid credentials THEN the Toolkit SHALL reject the authentication attempt and increment the failed login counter
3. WHEN a user exceeds five failed login attempts THEN the Toolkit SHALL lock the account for fifteen minutes
4. WHEN a user session is created THEN the Toolkit SHALL generate a JWT token with a thirty-minute expiration
5. WHEN a JWT token expires THEN the Toolkit SHALL require re-authentication before allowing further actions

### Requirement 2

**User Story:** As a security-conscious user, I want to enable multi-factor authentication, so that my account has additional protection beyond passwords

#### Acceptance Criteria

1. WHEN a user enables MFA THEN the Toolkit SHALL generate a TOTP secret and display a QR code for authenticator app enrollment
2. WHEN a user with MFA enabled submits valid credentials THEN the Toolkit SHALL prompt for an MFA verification code before completing authentication
3. WHEN a user submits a valid MFA code within the thirty-second time window THEN the Toolkit SHALL complete the authentication process
4. WHEN a user submits an invalid MFA code THEN the Toolkit SHALL reject the authentication attempt and allow two additional retry attempts
5. WHERE MFA is enabled via SMS or email, WHEN a user requests an MFA code THEN the Toolkit SHALL deliver the code within sixty seconds

### Requirement 3

**User Story:** As an administrator, I want to integrate with our corporate SSO system, so that users can authenticate using existing organizational credentials

#### Acceptance Criteria

1. WHERE SSO integration is configured, WHEN a user initiates login THEN the Toolkit SHALL redirect to the configured identity provider
2. WHEN the identity provider returns a valid SAML assertion THEN the Toolkit SHALL create a user session with appropriate role mappings
3. WHEN the identity provider returns a valid OAuth token THEN the Toolkit SHALL validate the token and create a user session
4. WHERE OpenID Connect is configured, WHEN a user completes authentication THEN the Toolkit SHALL extract user claims and create a session
5. WHEN SSO authentication fails THEN the Toolkit SHALL display an error message and provide a fallback to local authentication

### Requirement 4

**User Story:** As a customer, I want to validate my license key after authentication, so that I can access the capabilities I am entitled to deploy

#### Acceptance Criteria

1. WHEN a user completes authentication THEN the Toolkit SHALL prompt for a License Key before granting access to capabilities
2. WHEN a user submits a License Key THEN the Toolkit SHALL validate the key against the license validation service
3. WHEN a License Key is valid THEN the Toolkit SHALL retrieve the entitlement list and unlock access to entitled capabilities
4. WHEN a License Key is invalid or expired THEN the Toolkit SHALL reject the key and display an error message with expiration details
5. WHEN a License Key has a user count limit THEN the Toolkit SHALL enforce the limit and reject authentication attempts that exceed the licensed user count
6. WHEN a License Key is validated THEN the Toolkit SHALL cache the entitlement list for the duration of the user session
7. WHEN a user attempts to deploy a capability THEN the Toolkit SHALL verify the capability is included in the cached entitlement list before proceeding

### Requirement 5

**User Story:** As an administrator, I want to assign roles to users, so that I can control what actions each user can perform in the toolkit

#### Acceptance Criteria

1. WHEN an Administrator assigns a role to a user THEN the Toolkit SHALL store the role assignment and apply it to all subsequent user sessions
2. WHEN a user with Administrator role accesses the Toolkit THEN the Toolkit SHALL grant full access to all capabilities, configurations, and audit logs
3. WHEN a user with Operator role accesses the Toolkit THEN the Toolkit SHALL grant deployment permissions for assigned environments only
4. WHEN a user with Viewer role accesses the Toolkit THEN the Toolkit SHALL grant read-only access to dashboards, reports, and non-sensitive logs
5. WHEN a user attempts an action not permitted by their role THEN the Toolkit SHALL deny the action and log the authorization failure

### Requirement 6

**User Story:** As a user, I want to view all available capabilities in a dashboard, so that I can understand what business functions I can deploy

#### Acceptance Criteria

1. WHEN a user accesses the capability dashboard THEN the Toolkit SHALL display all capabilities with their deployment status, description, and business value
2. WHEN a capability is entitled by the user's license THEN the Toolkit SHALL mark the capability as available for deployment
3. WHEN a capability is not entitled by the user's license THEN the Toolkit SHALL mark the capability as unavailable and display upgrade information
4. WHEN a capability is already deployed THEN the Toolkit SHALL display the deployment status and environment information
5. WHEN a user selects a capability THEN the Toolkit SHALL display detailed documentation, sample demos, and deployment options

### Requirement 7

**User Story:** As an operator, I want to deploy a capability using a guided wizard, so that I can provision infrastructure without manual configuration

#### Acceptance Criteria

1. WHEN an Operator selects a capability for deployment THEN the Toolkit SHALL launch a deployment wizard with step-by-step guidance
2. WHEN the wizard prompts for deployment mode THEN the Toolkit SHALL offer options for customer infrastructure or SaaS-hosted deployment
3. WHEN the wizard prompts for target environment THEN the Toolkit SHALL display configured environments and allow selection
4. WHEN the wizard prompts for configuration parameters THEN the Toolkit SHALL validate all inputs against the capability requirements
5. WHEN all wizard steps are completed THEN the Toolkit SHALL initiate the deployment and display real-time progress updates
6. WHEN a deployment completes successfully THEN the Toolkit SHALL display the CloudFormation stack outputs and capability endpoints
7. WHEN a deployment fails THEN the Toolkit SHALL display error details and offer rollback or retry options

### Requirement 8

**User Story:** As an administrator, I want to configure multiple isolated environments, so that I can manage development, staging, and production deployments separately

#### Acceptance Criteria

1. WHEN an Administrator creates an environment THEN the Toolkit SHALL store the environment configuration with unique identifiers
2. WHEN an environment is configured THEN the Toolkit SHALL require AWS region, credentials, and IAM role specifications
3. WHEN a capability is deployed to an environment THEN the Toolkit SHALL isolate the deployment from other environments
4. WHEN a user views deployment history THEN the Toolkit SHALL display deployments grouped by environment
5. WHEN an environment is deleted THEN the Toolkit SHALL prevent deletion if active deployments exist in that environment

### Requirement 9

**User Story:** As an operator, I want to monitor deployed capabilities, so that I can ensure they are healthy and performing correctly

#### Acceptance Criteria

1. WHEN a capability is deployed THEN the Toolkit SHALL perform health checks every five minutes and display the status
2. WHEN a health check fails THEN the Toolkit SHALL send an alert notification to configured recipients
3. WHEN an Operator views capability metrics THEN the Toolkit SHALL display CloudWatch metrics for the deployed resources
4. WHEN an Operator requests logs THEN the Toolkit SHALL retrieve logs from CloudWatch and display them in the interface
5. WHEN logs are requested for download THEN the Toolkit SHALL generate a downloadable log archive in JSON or text format

### Requirement 10

**User Story:** As an administrator, I want to apply patches to deployed capabilities, so that I can keep systems up-to-date with security fixes and improvements

#### Acceptance Criteria

1. WHEN a new capability version is available THEN the Toolkit SHALL display a notification in the dashboard
2. WHEN an Administrator selects a capability for patching THEN the Toolkit SHALL display the current version, available version, and release notes
3. WHEN an Administrator initiates a patch THEN the Toolkit SHALL create a CloudFormation change set and display the proposed changes
4. WHEN an Administrator approves the change set THEN the Toolkit SHALL execute the patch deployment and track progress
5. WHEN a patch fails THEN the Toolkit SHALL automatically roll back to the previous version and log the failure details
6. WHEN a patch completes successfully THEN the Toolkit SHALL update the capability version in the deployment metadata

### Requirement 11

**User Story:** As a user, I want to access the toolkit as a Progressive Web Application, so that I can use it on any device with a modern browser

#### Acceptance Criteria

1. WHEN a user accesses the Toolkit URL in a browser THEN the Toolkit SHALL load as a PWA with service worker registration
2. WHEN a user installs the PWA THEN the Toolkit SHALL add an application icon to the device home screen or desktop
3. WHEN the user is offline THEN the Toolkit SHALL display cached documentation and deployment status using service workers
4. WHEN the user regains connectivity THEN the Toolkit SHALL synchronize any pending actions and refresh data
5. WHEN a new version is deployed THEN the Toolkit SHALL prompt the user to refresh and load the updated application

### Requirement 12

**User Story:** As a user, I want to install the toolkit as a desktop application, so that I can have native OS integration and enhanced functionality

#### Acceptance Criteria

1. WHEN a user downloads the Electron installer THEN the Toolkit SHALL provide platform-specific installers for Windows, macOS, and Linux
2. WHEN the desktop application launches THEN the Toolkit SHALL display in a native window with system tray integration
3. WHEN the desktop application receives a notification THEN the Toolkit SHALL display a native OS notification
4. WHEN a new version is available THEN the Toolkit SHALL automatically download and prompt the user to install the update
5. WHEN the desktop application accesses the file system THEN the Toolkit SHALL use native file dialogs for log downloads and configuration imports

### Requirement 13

**User Story:** As a compliance officer, I want all user actions to be logged, so that I can audit system usage and investigate security incidents

#### Acceptance Criteria

1. WHEN a user performs any action THEN the Toolkit SHALL log the action to CloudTrail with timestamp, user identity, and action details
2. WHEN an authentication event occurs THEN the Toolkit SHALL log the event with IP address, user agent, and authentication result
3. WHEN a deployment is initiated THEN the Toolkit SHALL log the deployment request with capability, environment, and configuration parameters
4. WHEN an Administrator views audit logs THEN the Toolkit SHALL display logs with filtering by user, action type, and time range
5. WHEN audit logs are exported THEN the Toolkit SHALL generate a tamper-evident export in CSV or JSON format with cryptographic signatures

### Requirement 14

**User Story:** As an administrator, I want the toolkit to check for new capabilities automatically, so that I can discover and deploy new features without vendor intervention

#### Acceptance Criteria

1. WHEN the Toolkit starts THEN the Toolkit SHALL check the configured artifact repository for capability updates
2. WHEN new capabilities are available THEN the Toolkit SHALL display them in the dashboard with a "New" indicator
3. WHEN the Administrator configures automatic sync THEN the Toolkit SHALL check for updates every twenty-four hours
4. WHEN the Administrator configures manual approval THEN the Toolkit SHALL require explicit approval before displaying new capabilities
5. WHERE GitHub integration is configured, WHEN a new release is published THEN the Toolkit SHALL retrieve the release artifacts and update the capability catalog

### Requirement 15

**User Story:** As a user, I want the toolkit to enforce password security policies, so that accounts are protected from weak credentials

#### Acceptance Criteria

1. WHEN a user creates a password THEN the Toolkit SHALL require a minimum of twelve characters with uppercase, lowercase, numbers, and special characters
2. WHEN a user changes their password THEN the Toolkit SHALL prevent reuse of the previous five passwords
3. WHEN a password is ninety days old THEN the Toolkit SHALL prompt the user to change their password at next login
4. WHEN a user enters a password THEN the Toolkit SHALL hash the password using Argon2 before storage
5. WHEN a user account is created THEN the Toolkit SHALL require password change on first login

### Requirement 16

**User Story:** As an operator, I want to receive notifications for deployment events, so that I can respond quickly to issues

#### Acceptance Criteria

1. WHEN a deployment completes successfully THEN the Toolkit SHALL send a notification to configured recipients via email or SMS
2. WHEN a deployment fails THEN the Toolkit SHALL send an alert notification with error details and recommended actions
3. WHEN a health check fails THEN the Toolkit SHALL send an alert notification within two minutes of detection
4. WHEN an Administrator configures notification preferences THEN the Toolkit SHALL allow selection of notification channels and event types
5. WHERE push notifications are enabled, WHEN an event occurs THEN the Toolkit SHALL deliver a push notification to the PWA or desktop application

### Requirement 17

**User Story:** As a developer, I want the toolkit to validate AWS permissions before deployment, so that I can identify configuration issues early

#### Acceptance Criteria

1. WHEN a deployment is initiated THEN the Toolkit SHALL validate AWS credentials have required IAM permissions before proceeding
2. WHEN IAM permissions are insufficient THEN the Toolkit SHALL display the missing permissions and provide documentation links
3. WHEN AWS credentials are invalid THEN the Toolkit SHALL reject the deployment and prompt for credential correction
4. WHEN a deployment requires cross-account access THEN the Toolkit SHALL validate the trust relationship and assume-role permissions
5. WHEN permission validation completes successfully THEN the Toolkit SHALL proceed with CloudFormation template generation

### Requirement 18

**User Story:** As an administrator, I want to manage API keys for programmatic access, so that I can integrate the toolkit with automation systems

#### Acceptance Criteria

1. WHEN an Administrator creates an API key THEN the Toolkit SHALL generate a cryptographically secure key and display it once
2. WHEN an API key is used THEN the Toolkit SHALL validate the key and apply the associated user's role permissions
3. WHEN an API key is revoked THEN the Toolkit SHALL immediately invalidate the key and reject subsequent requests
4. WHEN an Administrator views API keys THEN the Toolkit SHALL display key metadata without revealing the key value
5. WHEN an API key is created THEN the Toolkit SHALL allow setting an expiration date and scope restrictions

### Requirement 19

**User Story:** As an administrator, I want to create and configure landing zones, so that I can establish foundational infrastructure for capability deployments

#### Acceptance Criteria

1. WHEN an Administrator creates a landing zone THEN the Toolkit SHALL store the landing zone configuration with unique identifiers and cloud provider details
2. WHEN a landing zone is configured for AWS THEN the Toolkit SHALL require VPC configuration, security groups, IAM roles, and region specifications
3. WHEN a landing zone is configured for Azure THEN the Toolkit SHALL require resource group, virtual network, network security groups, and region specifications
4. WHEN a landing zone is configured for Google Cloud THEN the Toolkit SHALL require project ID, VPC network, firewall rules, and region specifications
5. WHEN a landing zone is configured for on-premise Kubernetes THEN the Toolkit SHALL require cluster endpoint, authentication credentials, and namespace specifications
6. WHEN a landing zone is configured for on-premise Ray cluster THEN the Toolkit SHALL require cluster endpoint, authentication credentials, and resource allocation specifications
7. WHEN an Administrator views landing zones THEN the Toolkit SHALL display all configured landing zones with their cloud provider type and status

### Requirement 20

**User Story:** As an administrator, I want to create product enclaves within landing zones, so that I can establish isolated environments for deploying capabilities

#### Acceptance Criteria

1. WHEN an Administrator creates a product enclave THEN the Toolkit SHALL require selection of a parent landing zone and store the enclave configuration
2. WHEN a product enclave is created in AWS THEN the Toolkit SHALL provision isolated subnets, security groups, and IAM roles within the landing zone VPC
3. WHEN a product enclave is created in Azure THEN the Toolkit SHALL provision isolated subnets and network security groups within the landing zone virtual network
4. WHEN a product enclave is created in Google Cloud THEN the Toolkit SHALL provision isolated subnets and firewall rules within the landing zone VPC network
5. WHEN a product enclave is created in Kubernetes THEN the Toolkit SHALL create a dedicated namespace with resource quotas and network policies
6. WHEN a product enclave is created in Ray cluster THEN the Toolkit SHALL allocate dedicated compute resources and establish resource isolation
7. WHEN an Administrator views product enclaves THEN the Toolkit SHALL display all enclaves grouped by their parent landing zone with deployment status

### Requirement 21

**User Story:** As an operator, I want to deploy capabilities into product enclaves using drag-and-drop, so that I can quickly provision business functions without complex configuration

#### Acceptance Criteria

1. WHEN an Operator views the deployment interface THEN the Toolkit SHALL display the capability catalog on one side and product enclaves on the other side
2. WHEN an Operator drags a capability from the catalog THEN the Toolkit SHALL highlight compatible product enclaves that can host the capability
3. WHEN an Operator drops a capability onto a product enclave THEN the Toolkit SHALL validate the capability is entitled by the license before proceeding
4. WHEN a capability is dropped onto a product enclave THEN the Toolkit SHALL launch a deployment wizard with pre-filled enclave configuration
5. WHEN a capability deployment is initiated via drag-and-drop THEN the Toolkit SHALL provision the capability infrastructure within the selected product enclave
6. WHEN a capability is successfully deployed to a product enclave THEN the Toolkit SHALL display the capability as deployed within the enclave visualization
7. WHEN an Operator views a product enclave THEN the Toolkit SHALL display all capabilities deployed within that enclave with their health status

### Requirement 22

**User Story:** As an administrator, I want to manage the lifecycle of landing zones and product enclaves, so that I can maintain and update infrastructure configurations

#### Acceptance Criteria

1. WHEN an Administrator attempts to delete a landing zone THEN the Toolkit SHALL prevent deletion if any product enclaves exist within the landing zone
2. WHEN an Administrator attempts to delete a product enclave THEN the Toolkit SHALL prevent deletion if any capabilities are deployed within the enclave
3. WHEN an Administrator updates a landing zone configuration THEN the Toolkit SHALL validate the changes and apply them to the underlying infrastructure
4. WHEN an Administrator updates a product enclave configuration THEN the Toolkit SHALL validate the changes do not conflict with deployed capabilities
5. WHEN a landing zone or product enclave is modified THEN the Toolkit SHALL log the change to the audit trail with user identity and timestamp

### Requirement 23

**User Story:** As an operator, I want to view the deployment topology, so that I can understand the relationship between landing zones, product enclaves, and deployed capabilities

#### Acceptance Criteria

1. WHEN an Operator accesses the topology view THEN the Toolkit SHALL display a hierarchical visualization of landing zones containing product enclaves containing capabilities
2. WHEN an Operator selects a landing zone in the topology THEN the Toolkit SHALL highlight all product enclaves and capabilities within that landing zone
3. WHEN an Operator selects a product enclave in the topology THEN the Toolkit SHALL display detailed information about the enclave and its deployed capabilities
4. WHEN an Operator selects a capability in the topology THEN the Toolkit SHALL display capability details, health status, and operational metrics
5. WHEN the topology view is displayed THEN the Toolkit SHALL use visual indicators to show health status for each landing zone, product enclave, and capability
