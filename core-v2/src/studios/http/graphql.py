from ariadne import gql


type_defs = gql("""
    input BatchUserInput {
        username: String!
        password: String!
        email: String!            
    }
                
    input CreateUserInput {
        username: String!
        password: String!
        email: String
        firstName: String
        lastName: String
        intro: String
        token: String
    }
                
    input ResetPasswordInput {
        email: String!
        token: String!
        password: String
    }
            
    input UpdateUserInput {
        id: ID!
        username: String
        password: String
        email: String
        binName: String
        role: Int
        firstName: String
        lastName: String
        displayName: String
        active: Boolean
        firebasePushnotId: String
        uploadLimit: Int
        intro: String
    }
    
    input MediaTableInput {
        page: Int
        limit: Int
        sort: [AssetSortEnum]
        name: String
        mediaTypes: [String]
        owners: [String]
        stages: [ID]
        tags: [String]
        createdBetween: [Date]
    }
                
    input LoginInput {
        username: String!
        password: String!
    }

    input ChangePasswordInput {
        oldPassword: String!
        newPassword: String!
        id: ID!
    }
    
    input SendEmailInput {
        subject: String!
        body: String!
        recipients: String!
        bcc: String
    }
    
  input SaveMediaInput {
        id: ID
        name: String!
        mediaType: String!
        copyrightLevel: Int!
        owner: String!
        stageIds: [ID!]!
        userIds: [ID!]
        tags: [String!]
        w: Float!
        h: Float!
        note: String
        urls: [String!]!
        voice: VoiceInput
        link: LinkInput
    }

    input VoiceInput {
        voice: String
        variant: String
        pitch: Int
        speed: Int
        amplitude: Int
    }

    input LinkInput {
        url: String
        blank: Boolean
        effect: Boolean
    }
            
    input LicenseInput {
        assetId: ID!
        level: Int!
        permissions: String!
    }
    
    input EmailInput {
        subject: String!
        body: String!
        recipients: [String!]
        cc: [String!]
        bcc: [String!]
        filenames: [String!]
    }
                
    input CreateSubscriptionInput {
        cardNumber: String!
        expYear: String!
        expMonth: String!
        cvc: String!
        amount: Float!
        currency: String!
        email: String!
        type: String!
    }

    input OneTimePurchaseInput {
        cardNumber: String!
        expYear: String!
        expMonth: String!
        cvc: String!
        amount: Float!
    }
    
                    
    input RecordInput {
        stageId: ID!
        name: String!
        description: String 
    }
                
    input PerformanceInput {
        id: ID!
        name: String!
        description: String
    }
    
    input SceneInput {
        name: String
        preview: String
        payload: String
        stageId: ID
    }
    
    input SearchStageInput {
        page: Int
        limit: Int
        sort: [StageSortEnum]
        name: String
        owners: [String]
        createdBetween: [Date]
    }
                
     input AssignMediaInput {
        id: ID!
        mediaIds: [ID]
    }
                
    input StageInput {
        id: ID
        fileLocation: String
        status: String
        visibility: Boolean
        cover: String
        name: String
        description: String
        playerAccess: String
        config: String
    }
                
    input UpdateMediaInput {
        id: ID!
        name: String!
        mediaType: String
        description: String
        fileLocation: String
        base64: String
        copyrightLevel: Int
        playerAccess: String
        uploadedFrames: [String]
    }
                
    input SystemEmailInput {
        subject: String!
        body: String!
        recipients: String!
        bcc: String
    }
                
    input ConfigInput {
        name: String!
        value: String!  
    }


    input UploadMediaInput {
        name: String!
        base64: String!
        mediaType: String!
        filename: String!
    }
                
    input AssignStagesInput {
        id: ID!
        stageIds: [ID!]
    }
                
   type StagesResponse {
        totalCount: Int
        edges: [Stage]
    }
            
    type SweepResponse {
        success: Boolean
        performanceId: ID
    }
                      
    type AdminPlayerConnection {
        totalCount: Int!
        edges: [User!]!
    }   

    type NginxConfig {
        limit: Int!            
    }
            
        
    type Tag {
        id: ID!
        name: String!
        color: String
        createdOn: Date  
    }
                
    type RefreshTokenResponse {
        access_token: String!
        refresh_token: String!
    }
    
    type User {
        id: ID!
        username: String!
        password: String
        email: String
        binName: String
        role: String
        firstName: String
        lastName: String
        displayName: String
        active: Boolean
        createdOn: String
        firebasePushnotId: String
        deactivatedOn: String
        uploadLimit: Int
        intro: String
        canSendEmail: Boolean
        lastLogin: String
        roleName: String
    }
                
    type Asset {
        id: ID!
        name: String
        src: String
        sign: String
        createdOn: Date
        size: Int!
        description: String
        assetType: AssetType
        owner: User
        stages: [Stage]
        tags: [String]
        copyrightLevel: Int
        permissions: [Permission]
        privilege: String
    }     

    type AssetConnection {
        totalCount: Int!
        edges: [Asset!]!
    }
            
                
    type Permission {
        id: ID!
        userId: Int!
        assetId: Int!
        approved: Boolean!
        seen: Boolean!
        createdOn: Date!
        note: String
        user: User!
    }
                
    type AssetType {
        id: ID
        name: String!
    }

    type Stage {
        id: ID!
        name: String
        fileLocation: String
        status: String
        visibility: Boolean
        cover: String
        description: String
        playerAccess: String    
        permission: String
        owner: User
        assets: [Asset]        
        createdOn: Date
    }
                
        type PerformanceCommunication {
        id: ID!
        ownerId: ID!
        ipAddress: String!
        websocketPort: Int!
        webclientPort: Int!
        topicName: String!
        username: String!
        password: String!
        createdOn: String!
        expiresOn: String
        performanceConfigId: Int!
    }
                
    type PerformanceConfig {
        id: ID!
        name: String!
        ownerId: ID!
        description: String!
        splashScreenText: String
        splashScreenAnimationUrls: String
        createdOn: String!
        expiresOn: String
    }   

    type Scene {
        id: ID!
        name: String!
        ownerId: ID!
        description: String!
        splashScreenText: String
        splashScreenAnimationUrls: String
        createdOn: String!
        expiresOn: String
    }   
                
    type ParentStage {
        id: ID!
        stageId: ID!
        childAssetId: ID!
        stage: Stage!
        childAsset: Asset!
    }
               
    type CreateUserPayload {
        user: User
    }
    
    type TokenType {
        user_id: Int
        access_token: String
        refresh_token: String
        role: Int
        first_name: String
        groups: [GroupType]
        username: String
        title: String
    }
    
    type GroupType {
        id: Int
        name: String
    }
            

    type License {
        id: ID!
        assetId: ID!
        createdOn: Date
        level: Int!
        permissions: String!
        assetPath: String
    }
    
                
    type ConfirmPermissionResponse {
        success: Boolean
        permissions: [Permission]
    }
                
    type Size {
        size: Int
    }
                       
    type BatchUserCreationPayload {
        users: [User!]!
    }
                
    type CommonResponse {
        success: Boolean
        message: String
    }
                
     fragment permissionFragment on Permission {
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

    fragment f1 on User {
        id
        username
        password
        email
        binName
        role
        firstName
        lastName
        displayName
        active
        createdOn
        firebasePushnotId
        deactivatedOn
        uploadLimit
        intro
        canSendEmail
        lastLogin
        roleName
    }
                
    type File {
        url: String!
    }

    type SaveMediaPayload {
        asset: Asset!
    }
                
    type DeleteMediaPayload {
        success: Boolean!
        message: String!
    }
        
    type EmailResponse {
        success: Boolean!
    }
                
    type UpdateStageResponse {
        result: String
    }
                
    type Performance {
        id: ID!
        name: String
        description: String
        stageId: ID!
        stage: Stage
        createdOn: Date
        savedOn: Date
        recording: Boolean
    }
                
        type Config{
        id: Int!
        name: String!
        value: String
        createdOn: Date
    }
                
    type SystemConfig {
        termsOfService: Config
        manual: Config
        esp: Config
        enableDonate: Config    
    }
                
    type FoyerConfig {
        title: Config
        description: Config
        menu: Config
        showRegistration: Config
    }

    scalar Date

    enum AssetSortEnum {
        ASSET_TYPE_ID_ASC
        ASSET_TYPE_ID_DESC
        OWNER_ID_ASC
        OWNER_ID_DESC
        NAME_ASC
        NAME_DESC
        CREATED_ON_ASC
        CREATED_ON_DESC
    }
    
    enum AdminPlayerSortEnum {
        USERNAME_ASC
        USERNAME_DESC
        CREATED_ON_ASC
        CREATED_ON_DESC
        LAST_LOGIN_ASC
        LAST_LOGIN_DESC
        ROLE_ASC
        ROLE_DESC
        EMAIL_ASC
        EMAIL_DESC
    }
                
    enum StageSortEnum {
        ASSET_TYPE_ID_ASC
        ASSET_TYPE_ID_DESC
        OWNER_ID_ASC
        OWNER_ID_DESC
        NAME_ASC
        NAME_DESC
        CREATED_ON_ASC
        CREATED_ON_DESC
    }
                
    type Mutation { 
        batchUserCreation(users: [BatchUserInput]!): BatchUserCreationPayload
        updateUser(input: UpdateUserInput!): User
        deleteUser(id: ID!): CommonResponse
        uploadFile(base64: String!, filename: String!): File!
        saveMedia(input: SaveMediaInput!): SaveMediaPayload!
        deleteMedia(id: ID!): DeleteMediaPayload!
        sendEmail(input: SendEmailInput!): CommonResponse
        changePassword(input: ChangePasswordInput!): CommonResponse
        calcSizes: Size
        confirmPermission(id: ID!, approved: Boolean): ConfirmPermissionResponse
        requestPermission(assetId: ID!, note: String): ConfirmPermissionResponse
        quickAssignMutation(stageId: ID!, assetId: ID!): CommonResponse,
        
        createUser(inbound: CreateUserInput!): CreateUserPayload
        requestPasswordReset(email: String!): CommonResponse
        verifyPasswordReset(input: ResetPasswordInput!): CommonResponse
        resetPassword(input: ResetPasswordInput!): CommonResponse    
                
        login(payload: LoginInput!): TokenType
        refreshToken: RefreshTokenResponse
        logout: String
                
        createLicense(input: LicenseInput!): License!
        revokeLicense(id: ID!): String!
                
        sendEmailExternal(emailInfo: EmailInput!): EmailResponse!
                
        oneTimePurchase(input: OneTimePurchaseInput!): CommonResponse
        createSubscription(input: CreateSubscriptionInput!): CommonResponse
        cancelSubscription(subscription_id: String!): CommonResponse
        updateEmailCustomer(customer_id: String!, email: String!): CommonResponse
                
        createStage(input: StageInput!): Stage
        updateStage(input: StageInput!): Stage
        duplicateStage(id: ID!, name: String!): Stage
        deleteStage(id: ID!): CommonResponse
        assignMedia(input: AssignMediaInput!): Asset
        uploadMedia(input: UploadMediaInput!): Asset
        updateMedia(input: UpdateMediaInput!): Asset
        deleteMediaOnStage(id: ID!): CommonResponse
        assignStages(input: AssignStagesInput!): Asset
        sweepStage(id: ID!): SweepResponse
        saveScene(input: SceneInput!): Scene
        deleteScene(id: ID!): CommonResponse
        updatePerformance(input: PerformanceInput!): CommonResponse
        deletePerformance(id: ID!): CommonResponse
        startRecording(input: RecordInput!): Performance
        saveRecording(id: ID!): Performance
        updateStatus(id: ID!): UpdateStageResponse
        updateVisibility(id: ID!): UpdateStageResponse   
        updateLastAccess(id: ID!): UpdateStageResponse   
                
        updateTermsOfService(url: String!): Config
        saveConfig(input: ConfigInput!): Config
        sendSystemEmail(input: SystemEmailInput!): CommonResponse
    }
                
    type Query {
        hello: String
        whoami: User
        adminPlayers(
            first: Int,
            page: Int,
            sort: [AdminPlayerSortEnum],
            usernameLike: String,
            createdBetween: [String]
        ): AdminPlayerConnection      
        media(input: MediaTableInput!): AssetConnection!  
        mediaList(mediaType: String, owner: String): [Asset!]!
        mediaTypes: [AssetType!]!
        tags: [Tag!]!
        users(active: Boolean): [User!]!
        getAllStages: [Stage!]!
                
        currentUser: User
                
        access(path: String!): License!
                
        performanceCommunication:  [PerformanceCommunication!]!
        performanceConfig: [PerformanceConfig!]!
        scene: [Scene!]!
        parentStage: [ParentStage!]
                
        stages(input: SearchStageInput): StagesResponse
        stage(id: ID!): Stage
        foyerStageList: [Stage!]!
                

        nginx: NginxConfig!
        system: SystemConfig!
        foyer: FoyerConfig!
    }      
""")
