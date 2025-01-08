# Upstage Setup Guide

This guide will help you set up and run the Upstage application using Docker.

## Setup OS

You need to install Docker, Nginx, and Certbot.

### 1. Debian

```sh
sh scripts/setup-os.sh
```

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

### 1. Configure Environment Variables

Go to the `config_formatted_date.py` file and update your environment variables as needed.

### 2. Start the Application

You can start the Upstage application using either a single container or multiple containers.

#### Single Container

To start the application using a single container, run the following command:

```sh
cd single-container
sh startup.sh
```

#### Multiple Containers

To start the application using multiple containers, use Docker Compose. First, ensure you have a `docker-compose.yml` file configured. Then, run the following command:

```sh
cd multiple-containers
docker-compose up -d
```

This will start all the services defined in your `docker-compose.yml` file.

### 3. Insert Seeding Data

- Exec into the backend container:

```sh
docker exec -it {upstage_backend_container_id} bash
```

- Set up environment variables:

```sh
export TIMESTAMP=$(date +"%d_%m_%Y")
```

- Create initial accounts:

Change default accounts by editing the following file:

```sh
vi src/users/scripts/create_test_users.py
```

After updating the information in this file, run the script to create accounts:

```sh
python3 -m src.users.scripts.create_test_users
```

- Create default data:

```sh
python3 -m src.stages.scripts.scaffold-base-media
```

Input variables:
- `/usr/app/uploads`: This is the default directory for `UPLOAD_USER_CONTENT_FOLDER` in `env.py`. If you modify this path, ensure to update the corresponding path in the docker-compose file as well.
- `{administrator_username}`: This placeholder should be replaced with the username of the administrator account created in the previous steps.

### 4. Application API Endpoints

- Endpoint: `domain.com/api/studio_graphql`

### Common Error Response Structure

In case of an error, the API will return a response with the following structure:

```json
{
    "data": {
        "operationName": null
    },
    "errors": [
        {
            "message": "Error message describing the issue.",
            "locations": [
                {
                    "line": lineNumber,
                    "column": columnNumber
                }
            ],
            "path": [
                "operationName"
            ],
            "extensions": {
                "exception": null
            }
        }
    ]
}
```

Example Error Response:

```json
{
    "data": {
        "login": null
    },
    "errors": [
        {
            "message": "Signature did not match digest. Please contact admin to make sure that cipher key is correctly set up.",
            "locations": [
                {
                    "line": 2,
                    "column": 3
                }
            ],
            "path": [
                "login"
            ],
            "extensions": {
                "exception": null
            }
        }
    ]
}
```
 
**currentUser**
Example Query:
```graphql
query {
    currentUser {
        id
        name
        email
    }
}
```

Example Response:
```json
{
    "data": {
        "currentUser": {
            "id": "1",
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
    }
}
```

**createUser**
Example Mutation:
```graphql
mutation {
    createUser(input: {
        name: "Jane Doe",
        email: "jane.doe@example.com",
        password: "password123"
    }) {
        user {
            id
            name
            email
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "createUser": {
            "user": {
                "id": "2",
                "name": "Jane Doe",
                "email": "jane.doe@example.com"
            }
        }
    }
}
```

**requestPasswordReset**
Example Mutation:
```graphql
mutation {
    requestPasswordReset(email: "jane.doe@example.com") {
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "requestPasswordReset": {
            "message": "Password reset link sent to your email."
        }
    }
}
```

**verifyPasswordReset**
Example Mutation:
```graphql
mutation {
    verifyPasswordReset(token: "reset-token") {
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "verifyPasswordReset": {
            "success": true
        }
    }
}
```

**resetPassword**
Example Mutation:
```graphql
mutation {
    resetPassword(token: "reset-token", newPassword: "newPassword123") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "resetPassword": {
            "success": true
        }
    }
}
```
**login**
Example Mutation:
```graphql
mutation {
    login(payload: {
        username: "user123",
        password: "password123"
    }) {
        user_id
        access_token
        refresh_token
        role
        first_name
        groups {
            id
            name
        }
        username
        title
    }
}
```

Example Response:
```json
{
    "data": {
        "login": {
            "user_id": 1,
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "role": 2,
            "first_name": "John",
            "groups": [
                {
                    "id": 1,
                    "name": "Admin"
                }
            ],
            "username": "user123",
            "title": "Mr."
        }
    }
}
```

**refreshToken**
Example Mutation:
```graphql
mutation {
    refreshToken {
        access_token
        refresh_token
    }
}
```

Example Response:
```json
{
    "data": {
        "refreshToken": {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh_token"
        }
    }
}
```

**logout**
Example Mutation:
```graphql
mutation {
    logout
}
```

Example Response:
```json
{
    "data": {
        "logout": "Successfully logged out"
    }
}
```

**stages**
Example Mutation:
```graphql
query {
    stages(input: SearchStageInput) {
        totalCount
        edges {
             id
            name
            fileLocation
            status
            visibility
            cover
            description
            playerAccess
            permission
            owner
            assets
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "stages": {
            "totalCount": 2,
            "edges": [
                {
                    "id": "1",
                    "name": "Stage One",
                    "fileLocation": "/path/to/file1",
                    "status": "active",
                    "visibility": true,
                    "cover": "cover1.png",
                    "description": "Description of Stage One",
                    "playerAccess": "public",
                    "permission": "read",
                    "owner": "owner1",
                    "assets": ["asset1", "asset2"]
                },
                {
                    "id": "2",
                    "name": "Stage Two",
                    "fileLocation": "/path/to/file2",
                    "status": "inactive",
                    "visibility": false,
                    "cover": "cover2.png",
                    "description": "Description of Stage Two",
                    "playerAccess": "private",
                    "permission": "write",
                    "owner": "owner2",
                    "assets": ["asset3", "asset4"]
                }
            ]
        }
    }
}
```

**stagebyid**
Example Query:
```graphql
query {
    stageById(id: "1") {
        id
        name
        description
        visibility
        createdOn
        updatedOn
    }
}
```

Example Response:
```json
{
    "data": {
        "stageById": {
            "id": "1",
            "name": "Stage One",
            "description": "Description of Stage One",
            "visibility": true,
            "createdOn": "2023-10-01",
            "updatedOn": "2023-10-02"
        }
    }
}
```


**createStage**
Example Mutation:
```graphql
mutation {
    createStage(input: {
        name: "New Stage",
        description: "Stage description",
        visibility: true
    }) {
        id
        name
        description
        visibility
    }
}
```

Example Response:
```json
{
    "data": {
        "createStage": {
            "id": "1",
            "name": "New Stage",
            "description": "Stage description",
            "visibility": true
        }
    }
}
```

**updateStage**

Example Mutation:
```graphql
mutation {
    updateStage(input: {
        id: "1",
        name: "Updated Stage",
        description: "Updated description"
    }) {
        id
        name
        description
    }
}
```

Example Response:
```json
{
    "data": {
        "updateStage": {
            "id": "1",
            "name": "Updated Stage",
            "description": "Updated description"
        }
    }
}
```

**duplicateStage**
Example Mutation:
```graphql
mutation {
    duplicateStage(id: "1", name: "Duplicate Stage") {
        id
        name
        description
    }
}
```

Example Response:
```json
{
    "data": {
        "duplicateStage": {
            "id": "2",
            "name": "Duplicate Stage",
            "description": "Stage description"
        }
    }
}
```

**deleteStage**
Example Mutation:
```graphql
mutation {
    deleteStage(id: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "deleteStage": {
            "success": true,
            "message": "Stage deleted successfully"
        }
    }
}
```

**assignMedia**
Example Mutation:
```graphql
mutation {
    assignMedia(input: {
        id: "1",
        mediaIds: ["1", "2"]
    }) {
        id
        name
    }
}
```

Example Response:
```json
{
    "data": {
        "assignMedia": {
            "id": "1",
            "name": "Media Name"
        }
    }
}
```

**uploadMedia**
Example Mutation:
```graphql
mutation {
    uploadMedia(input: {
        name: "New Media",
        base64: "base64string",
        mediaType: "image/png",
        filename: "media.png"
    }) {
        id
        name
        src
    }
}
```

Example Response:
```json
{
    "data": {
        "uploadMedia": {
            "id": "1",
            "name": "New Media",
            "src": "media.png"
        }
    }
}
```

**updateMedia**
Example Mutation:
```graphql
mutation {
    updateMedia(input: {
        id: "1",
        name: "Updated Media",
        description: "Updated description"
    }) {
        id
        name
        description
    }
}
```

Example Response:
```json
{
    "data": {
        "updateMedia": {
            "id": "1",
            "name": "Updated Media",
            "description": "Updated description"
        }
    }
}
```

**deleteMedia**
Example Mutation:
```graphql
mutation {
    deleteMedia(id: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "deleteMedia": {
            "success": true,
            "message": "Media deleted successfully"
        }
    }
}
```

**assignStages**
Example Mutation:
```graphql
mutation {
    assignStages(input: {
        id: "1",
        stageIds: ["1", "2"]
    }) {
        id
        name
    }
}
```

Example Response:
```json
{
    "data": {
        "assignStages": {
            "id": "1",
            "name": "Stage Name"
        }
    }
}
```

**sweepStage**
Example Mutation:
```graphql
mutation {
    sweepStage(id: "1") {
        success
        performanceId
    }
}
```

Example Response:
```json
{
    "data": {
        "sweepStage": {
            "success": true,
            "performanceId": "1"
        }
    }
}
```

**saveScene**
Example Mutation:
```graphql
mutation {
    saveScene(input: {
        name: "New Scene",
        stageId: "1"
    }) {
        id
        name
        stageId
    }
}
```

Example Response:
```json
{
    "data": {
        "saveScene": {
            "id": "1",
            "name": "New Scene",
            "stageId": "1"
        }
    }
}
```

**deleteScene**
Example Mutation:
```graphql
mutation {
    deleteScene(id: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "deleteScene": {
            "success": true,
            "message": "Scene deleted successfully"
        }
    }
}
```

**updatePerformance**
Example Mutation:
```graphql
mutation {
    updatePerformance(input: {
        id: "1",
        name: "Updated Performance"
    }) {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "updatePerformance": {
            "success": true,
            "message": "Performance updated successfully"
        }
    }
}
```

**deletePerformance**
Example Mutation:
```graphql
mutation {
    deletePerformance(id: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "deletePerformance": {
            "success": true,
            "message": "Performance deleted successfully"
        }
    }
}
```

**startRecording**
Example Mutation:
```graphql
mutation {
    startRecording(input: {
        stageId: "1",
        name: "New Recording"
    }) {
        id
        name
        stageId
    }
}
```

Example Response:
```json
{
    "data": {
        "startRecording": {
            "id": "1",
            "name": "New Recording",
            "stageId": "1"
        }
    }
}
```

**saveRecording**
Example Mutation:
```graphql
mutation {
    saveRecording(id: "1") {
        id
        name
        stageId
    }
}
```

Example Response:
```json
{
    "data": {
        "saveRecording": {
            "id": "1",
            "name": "Recording Name",
            "stageId": "1"
        }
    }
}
```

**updateStatus**
Example Mutation:
```graphql
mutation {
    updateStatus(id: "1") {
        result
    }
}
```

Example Response:
```json
{
    "data": {
        "updateStatus": {
            "result": "Status updated"
        }
    }
}
```

**updateVisibility**
Example Mutation:
```graphql
mutation {
    updateVisibility(id: "1") {
        result
    }
}
```

Example Response:
```json
{
    "data": {
        "updateVisibility": {
            "result": "Visibility updated"
        }
    }
}
```

**updateLastAccess**
Example Mutation:
```graphql
mutation {
    updateLastAccess(id: "1") {
        result
    }
}
```

Example Response:
```json
{
    "data": {
        "updateLastAccess": {
            "result": "Last access updated"
        }
    }
}
```

**sendEmailExternal**
Example Mutation:
```graphql
mutation {
    sendEmailExternal(emailInfo: {
        subject: "Meeting Reminder",
        body: "Don't forget about the meeting tomorrow at 10 AM.",
        recipients: ["john.doe@example.com"],
        cc: ["jane.doe@example.com"],
        bcc: ["manager@example.com"],
        filenames: ["agenda.pdf"]
    }) {
        success
    }
}
```

Example Response:
```json
{
    "data": {
        "sendEmailExternal": {
            "success": true
        }
    }
}
```

**access**
Example Query:
```graphql
query {
    access(path: "/path/to/asset") {
        id
        assetId
        createdOn
        level
        permissions
        assetPath
    }
}
```

Example Response:
```json
{
    "data": {
        "access": {
            "id": "1",
            "assetId": "123",
            "createdOn": "2023-10-01",
            "level": 1,
            "permissions": "read",
            "assetPath": "/path/to/asset"
        }
    }
}
```

**createLicense**
Example Mutation:
```graphql
mutation {
    createLicense(input: {
        assetId: "123",
        level: 1,
        permissions: "read"
    }) {
        id
        assetId
        createdOn
        level
        permissions
        assetPath
    }
}
```

Example Response:
```json
{
    "data": {
        "createLicense": {
            "id": "1",
            "assetId": "123",
            "createdOn": "2023-10-01",
            "level": 1,
            "permissions": "read",
            "assetPath": "/path/to/asset"
        }
    }
}
```

**revokeLicense**
Example Mutation:
```graphql
mutation {
    revokeLicense(id: "1") {
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "revokeLicense": "License revoked successfully"
    }
}
```

**performanceCommunication**
Example Query:
```graphql
query {
    performanceCommunication {
        id
        ownerId
        ipAddress
        websocketPort
        webclientPort
        topicName
        username
        password
        createdOn
        expiresOn
        performanceConfigId
    }
}
```

Example Response:
```json
{
    "data": {
        "performanceCommunication": [
            {
                "id": "1",
                "ownerId": "1",
                "ipAddress": "192.168.1.1",
                "websocketPort": 8080,
                "webclientPort": 3000,
                "topicName": "performance_topic",
                "username": "user",
                "password": "pass",
                "createdOn": "2023-10-01",
                "expiresOn": "2023-12-01",
                "performanceConfigId": 1
            }
        ]
    }
}
```

**performanceConfig**
Example Query:
```graphql
query {
    performanceConfig {
        id
        name
        ownerId
        description
        splashScreenText
        splashScreenAnimationUrls
        createdOn
        expiresOn
    }
}
```

Example Response:
```json
{
    "data": {
        "performanceConfig": [
            {
                "id": "1",
                "name": "Performance Config",
                "ownerId": "1",
                "description": "Description of the performance config",
                "splashScreenText": "Welcome",
                "splashScreenAnimationUrls": "http://example.com/animation",
                "createdOn": "2023-10-01",
                "expiresOn": "2023-12-01"
            }
        ]
    }
}
```

**scene**
Example Query:
```graphql
query {
    scene {
        id
        name
        ownerId
        description
        splashScreenText
        splashScreenAnimationUrls
        createdOn
        expiresOn
    }
}
```

Example Response:
```json
{
    "data": {
        "scene": [
            {
                "id": "1",
                "name": "Scene Name",
                "ownerId": "1",
                "description": "Description of the scene",
                "splashScreenText": "Welcome",
                "splashScreenAnimationUrls": "http://example.com/animation",
                "createdOn": "2023-10-01",
                "expiresOn": "2023-12-01"
            }
        ]
    }
}
```

**parentStage**
Example Query:
```graphql
query {
    parentStage {
        id
        stageId
        childAssetId
        stage {
            id
            name
            description
            createdOn
            expiresOn
            assets {
                id
                stageId
                childAssetId
            }
        }
        childAsset {
            id
            name
            type
            createdOn
            expiresOn
            stages {
                id
                stageId
                childAssetId
            }
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "parentStage": [
            {
                "id": "1",
                "stageId": "1",
                "childAssetId": "1",
                "stage": {
                    "id": "1",
                    "name": "Stage Name",
                    "description": "Description of the stage",
                    "createdOn": "2023-10-01",
                    "expiresOn": "2023-12-01",
                    "assets": [
                        {
                            "id": "1",
                            "stageId": "1",
                            "childAssetId": "1"
                        }
                    ]
                },
                "childAsset": {
                    "id": "1",
                    "name": "Asset Name",
                    "type": "image",
                    "createdOn": "2023-10-01",
                    "expiresOn": "2023-12-01",
                    "stages": [
                        {
                            "id": "1",
                            "stageId": "1",
                            "childAssetId": "1"
                        }
                    ]
                }
            }
        ]
    }
}
```
**nginx**
Example Query:
```graphql
query {
    nginx {
        limit
    }
}
```

Example Response:
```json
{
    "data": {
        "nginx": {
            "limit": 100
        }
    }
}
```

**system**
Example Query:
```graphql
query {
    system {
        termsOfService {
            id
            name
            value
            createdOn
        }
        manual {
            id
            name
            value
            createdOn
        }
        esp {
            id
            name
            value
            createdOn
        }
        enableDonate {
            id
            name
            value
            createdOn
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "system": {
            "termsOfService": {
                "id": 1,
                "name": "Terms of Service",
                "value": "http://example.com/tos",
                "createdOn": "2023-10-01"
            },
            "manual": {
                "id": 2,
                "name": "User Manual",
                "value": "http://example.com/manual",
                "createdOn": "2023-10-01"
            },
            "esp": {
                "id": 3,
                "name": "ESP Config",
                "value": "Enabled",
                "createdOn": "2023-10-01"
            },
            "enableDonate": {
                "id": 4,
                "name": "Enable Donate",
                "value": "true",
                "createdOn": "2023-10-01"
            }
        }
    }
}
```

**foyer**
Example Query:
```graphql
query {
    foyer {
        title {
            id
            name
            value
            createdOn
        }
        description {
            id
            name
            value
            createdOn
        }
        menu {
            id
            name
            value
            createdOn
        }
        showRegistration {
            id
            name
            value
            createdOn
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "foyer": {
            "title": {
                "id": 1,
                "name": "Foyer Title",
                "value": "Welcome to the Foyer",
                "createdOn": "2023-10-01"
            },
            "description": {
                "id": 2,
                "name": "Foyer Description",
                "value": "This is the foyer description.",
                "createdOn": "2023-10-01"
            },
            "menu": {
                "id": 3,
                "name": "Foyer Menu",
                "value": "Home, About, Contact",
                "createdOn": "2023-10-01"
            },
            "showRegistration": {
                "id": 4,
                "name": "Show Registration",
                "value": "true",
                "createdOn": "2023-10-01"
            }
        }
    }
}
```

**updateTermsOfService**
Example Mutation:
```graphql
mutation {
    updateTermsOfService(url: "http://example.com/new-tos") {
        id
        name
        value
        createdOn
    }
}
```

Example Response:
```json
{
    "data": {
        "updateTermsOfService": {
            "id": 1,
            "name": "Terms of Service",
            "value": "http://example.com/new-tos",
            "createdOn": "2023-10-01"
        }
    }
}
```

**saveConfig**
Example Mutation:
```graphql
mutation {
    saveConfig(input: {
        name: "New Config",
        value: "Config Value"
    }) {
        id
        name
        value
        createdOn
    }
}
```

Example Response:
```json
{
    "data": {
        "saveConfig": {
            "id": 1,
            "name": "New Config",
            "value": "Config Value",
            "createdOn": "2023-10-01"
        }
    }
}
```

**sendEmail**
Example Mutation:
```graphql
mutation {
    sendEmail(input: {
        subject: "Test Email",
        body: "This is a test email.",
        recipients: "recipient@example.com",
        bcc: "bcc@example.com"
    }) {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "sendEmail": {
            "success": true,
            "message": "Email sent successfully"
        }
    }
}
```
**oneTimePurchase**
Example Mutation:
```graphql
mutation {
    oneTimePurchase(input: {
        cardNumber: "4242424242424242",
        expYear: "2023",
        expMonth: "12",
        cvc: "123",
        amount: 100.0
    }) {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "oneTimePurchase": {
            "success": true,
            "message": "Payment successful"
        }
    }
}
```

**createSubscription**
Example Mutation:
```graphql
mutation {
    createSubscription(input: {
        cardNumber: "4242424242424242",
        expYear: "2023",
        expMonth: "12",
        cvc: "123",
        amount: 50.0,
        currency: "USD",
        email: "user@example.com",
        type: "monthly"
    }) {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "createSubscription": {
            "success": true,
            "message": "Subscription created successfully"
        }
    }
}
```

**cancelSubscription**
Example Mutation:
```graphql
mutation {
    cancelSubscription(subscription_id: "sub_12345") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "cancelSubscription": {
            "success": true,
            "message": "Subscription cancelled successfully"
        }
    }
}
```

**updateEmailCustomer**
Example Mutation:
```graphql
mutation {
    updateEmailCustomer(customer_id: "cus_12345", email: "new.email@example.com") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "updateEmailCustomer": {
            "success": true,
            "message": "Customer email updated successfully"
        }
    }
}
```

**batchUserCreation**
Example Mutation:
```graphql
mutation {
    batchUserCreation(users: [
        {
            username: "user1",
            password: "password1",
            email: "user1@example.com"
        },
        {
            username: "user2",
            password: "password2",
            email: "user2@example.com"
        }
    ]) {
        users {
            id
            username
            email
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "batchUserCreation": {
            "users": [
                {
                    "id": "1",
                    "username": "user1",
                    "email": "user1@example.com"
                },
                {
                    "id": "2",
                    "username": "user2",
                    "email": "user2@example.com"
                }
            ]
        }
    }
}
```

**updateUser**
Example Mutation:
```graphql
mutation {
    updateUser(input: {
        id: "1",
        username: "updatedUser",
        email: "updated@example.com"
    }) {
        id
        username
        email
    }
}
```

Example Response:
```json
{
    "data": {
        "updateUser": {
            "id": "1",
            "username": "updatedUser",
            "email": "updated@example.com"
        }
    }
}
```

**deleteUser**
Example Mutation:
```graphql
mutation {
    deleteUser(id: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "deleteUser": {
            "success": true,
            "message": "User deleted successfully"
        }
    }
}
```

**uploadFile**
Example Mutation:
```graphql
mutation {
    uploadFile(base64: "base64string", filename: "file.png") {
        url
    }
}
```

Example Response:
```json
{
    "data": {
        "uploadFile": {
            "url": "http://example.com/file.png"
        }
    }
}
```

**saveMedia**
Example Mutation:
```graphql
mutation {
    saveMedia(input: {
        name: "New Media",
        mediaType: "image/png",
        copyrightLevel: 1,
        owner: "ownerId",
        stageIds: ["stageId1"],
        tags: ["tag1", "tag2"],
        w: 1920,
        h: 1080,
        urls: ["http://example.com/media.png"]
    }) {
        asset {
            id
            name
            src
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "saveMedia": {
            "asset": {
                "id": "1",
                "name": "New Media",
                "src": "http://example.com/media.png"
            }
        }
    }
}
```

**deleteMedia**
Example Mutation:
```graphql
mutation {
    deleteMedia(id: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "deleteMedia": {
            "success": true,
            "message": "Media deleted successfully"
        }
    }
}
```

**sendEmail**
Example Mutation:
```graphql
mutation {
    sendEmail(input: {
        subject: "Test Email",
        body: "This is a test email.",
        recipients: "recipient@example.com"
    }) {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "sendEmail": {
            "success": true,
            "message": "Email sent successfully"
        }
    }
}
```

**changePassword**
Example Mutation:
```graphql
mutation {
    changePassword(input: {
        oldPassword: "oldPassword123",
        newPassword: "newPassword123",
        id: "1"
    }) {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "changePassword": {
            "success": true,
            "message": "Password changed successfully"
        }
    }
}
```

**calcSizes**
Example Mutation:
```graphql
mutation {
    calcSizes {
        size
    }
}
```

Example Response:
```json
{
    "data": {
        "calcSizes": {
            "size": 1024
        }
    }
}
```

**confirmPermission**
Example Mutation:
```graphql
mutation {
    confirmPermission(id: "1", approved: true) {
        success
        permissions {
            id
            userId
            assetId
            approved
            seen
            createdOn
            note
            user {
                username
                displayName
            }
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "confirmPermission": {
            "success": true,
            "permissions": [
                {
                    "id": "1",
                    "userId": 1,
                    "assetId": 1,
                    "approved": true,
                    "seen": false,
                    "createdOn": "2023-10-01",
                    "note": "Permission note",
                    "user": {
                        "username": "user1",
                        "displayName": "User One"
                    }
                }
            ]
        }
    }
}
```

**requestPermission**
Example Mutation:
```graphql
mutation {
    requestPermission(assetId: "1", note: "Requesting permission") {
        success
        permissions {
            id
            userId
            assetId
            approved
            seen
            createdOn
            note
            user {
                username
                displayName
            }
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "requestPermission": {
            "success": true,
            "permissions": [
                {
                    "id": "1",
                    "userId": 1,
                    "assetId": 1,
                    "approved": false,
                    "seen": false,
                    "createdOn": "2023-10-01",
                    "note": "Requesting permission",
                    "user": {
                        "username": "user1",
                        "displayName": "User One"
                    }
                }
            ]
        }
    }
}
```

**quickAssignMutation**
Example Mutation:
```graphql
mutation {
    quickAssignMutation(stageId: "1", assetId: "1") {
        success
        message
    }
}
```

Example Response:
```json
{
    "data": {
        "quickAssignMutation": {
            "success": true,
            "message": "Asset assigned to stage successfully"
        }
    }
}
```

**whoami**
Example Query:
```graphql
query {
    whoami {
        id
        username
        email
    }
}
```

Example Response:
```json
{
    "data": {
        "whoami": {
            "id": "1",
            "username": "user1",
            "email": "user1@example.com"
        }
    }
}
```

**adminPlayers**
Example Query:
```graphql
query {
    adminPlayers(first: 10, page: 1, sort: [USERNAME_ASC]) {
        totalCount
        edges {
            id
            username
            email
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "adminPlayers": {
            "totalCount": 2,
            "edges": [
                {
                    "id": "1",
                    "username": "user1",
                    "email": "user1@example.com"
                },
                {
                    "id": "2",
                    "username": "user2",
                    "email": "user2@example.com"
                }
            ]
        }
    }
}
```

**media**
Example Query:
```graphql
query {
    media(input: { page: 1, limit: 10 }) {
        totalCount
        edges {
            id
            name
            src
        }
    }
}
```

Example Response:
```json
{
    "data": {
        "media": {
            "totalCount": 2,
            "edges": [
                {
                    "id": "1",
                    "name": "Media 1",
                    "src": "http://example.com/media1.png"
                },
                {
                    "id": "2",
                    "name": "Media 2",
                    "src": "http://example.com/media2.png"
                }
            ]
        }
    }
}
```

**mediaList**
Example Query:
```graphql
query {
    mediaList(mediaType: "image/png", owner: "owner1") {
        id
        name
        src
    }
}
```

Example Response:
```json
{
    "data": {
        "mediaList": [
            {
                "id": "1",
                "name": "Media 1",
                "src": "http://example.com/media1.png"
            },
            {
                "id": "2",
                "name": "Media 2",
                "src": "http://example.com/media2.png"
            }
        ]
    }
}
```

**tags**
Example Query:
```graphql
    query {
        tags {
            id
            name
            color
            createdOn
        }
    }
```

Example Response:
```json
{
  "data": {
    "tags": [
      {
        "id": "1",
        "name": "test",
        "color": null
      }
    ]
  }
}
```

**mediaTypes**
Example Query:
```graphql
    query {
        mediaTypes{
            id
            name
        }
    }
```

Example Response:
```json
{
  "data": {
    "mediaTypes": [
      {
        "id": "1",
        "name": "image"
      }
    ]
  }
}
```

**users**
Example Query:
```graphql
    query {
        users(active: true) {
            id
            username
            displayName
        }
    }
```

Example Response:
```json
{
  "data": {
    "users": [
      {
        "id": "203",
        "username": "updated_user",
        "displayName": null
      }
    ]
  }
}
```

**getAllStagesInStudio**
Example Query:
```graphql
    query {
        getAllStages {
            id
            username
            displayName
        }
    }
```

Example Response:
```json
{
 "data": {
    "getAllStages": [
      {
        "id": "2",
        "name": "Stage Name",
        "owner": {
          "username": "karen35@example.net",
          "displayName": ""
        },
        "createdOn": "2024-11-26T17:42:04.545183"
      }
    ]
    }
}
```


**foyerStageList**

Example Query:
```graphql
    query {
        foyerStageList {
            id
            name
            owner {
            displayName
            username
            }
            fileLocation
            cover
        }
    }
```

Example Response:
```json
{
  "data": {
    "foyerStageList": [
      {
        "id": "15",
        "name": "Duplicate Stage",
        "owner": {
          "displayName": "",
          "username": "brentle@example.net"
        },
        "fileLocation": "duplicate-stage1",
        "cover": null
      }
    ]
  }
}
```

**stageList**

Example Query:
```graphql
{
  stageList(
    input:{ fileLocation:"duplicate-stage17"}
  ) {
    id
    name
    fileLocation
    owner {
      id
      binName
      username
    }
     attributes {
      id
      name
      description
    }
    visibility
    status
    permission
    
  	assets {
      assetType {
        name
      }
      name
      id
      fileLocation
      description
    }
    scenes {
      id
      name
    }
  	events {
      id
      payload
      scenePreview
      mqttTimestamp
    }
  }
}
```

Example Response:
```json
{
  "data": {
    "stageList": [
      {
        "id": "69",
        "name": "Duplicate Stage",
        "fileLocation": "duplicate-stage17",
        "owner": {
          "id": "485",
          "binName": "",
          "username": "422lisa63@example.org"
        },
        "attributes": [
          {
            "id": "352",
            "name": "status",
            "description": "live"
          },
          {
            "id": "347",
            "name": "cover",
            "description": "http://example.com/cover.jpg"
          },
          {
            "id": "350",
            "name": "playerAccess",
            "description": "public"
          },
          {
            "id": "351",
            "name": "description",
            "description": "Description of the stage"
          },
          {
            "id": "348",
            "name": "visibility",
            "description": ""
          }
        ],
        "visibility": false,
        "status": "live",
        "permission": null,
        "assets": [
          {
            "assetType": {
              "name": "image"
            },
            "name": "test",
            "id": "31",
            "fileLocation": "image/a8423b526ce9418297249603e0788d47test.png",
            "description": null
          }
        ],
        "scenes": [],
        "events": []
      }
    ]
  }
}
```