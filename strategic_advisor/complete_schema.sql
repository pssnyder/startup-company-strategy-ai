-- COMPLETE STARTUP COMPANY GAME SAVE DATABASE SCHEMA
-- 100% coverage of all JSON schema fields

-- Main game state table (all root-level scalars)
CREATE TABLE IF NOT EXISTS game_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,

    -- Temporal tracking
    real_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_modified_time DATETIME,
    ingestion_order INTEGER,

    -- All root-level scalar fields from JSON schema
    date DATETIME, -- JSON: date (REQUIRED)
    started DATETIME, -- JSON: started (REQUIRED)
    gameover BOOLEAN, -- JSON: gameover (REQUIRED)
    state INTEGER, -- JSON: state (REQUIRED)
    paused BOOLEAN, -- JSON: paused (REQUIRED)
    lastVersion TEXT, -- JSON: lastVersion (REQUIRED)
    balance REAL, -- JSON: balance (REQUIRED)
    lastPricePerHour INTEGER, -- JSON: lastPricePerHour (REQUIRED)
    selectedFloor INTEGER, -- JSON: selectedFloor (REQUIRED)
    maxContractHours INTEGER, -- JSON: maxContractHours (REQUIRED)
    contractsCompleted INTEGER, -- JSON: contractsCompleted (REQUIRED)
    xp REAL, -- JSON: xp (REQUIRED)
    researchPoints INTEGER, -- JSON: researchPoints (REQUIRED)
    userLossEnabled BOOLEAN, -- JSON: userLossEnabled (REQUIRED)
    game_id TEXT, -- JSON: id (REQUIRED)
    betaVersionAtStart INTEGER, -- JSON: betaVersionAtStart (REQUIRED)
    companyName TEXT, -- JSON: companyName (REQUIRED)
    saveGameName TEXT, -- JSON: saveGameName (REQUIRED)
    fileName TEXT, -- JSON: fileName (REQUIRED)
    lastSaved DATETIME, -- JSON: lastSaved (REQUIRED)
    selectedBuildingName TEXT, -- JSON: selectedBuildingName (REQUIRED)
    needsNewLoan BOOLEAN, -- JSON: needsNewLoan (REQUIRED)
    amountOfAvailableResearchItems INTEGER, -- JSON: amountOfAvailableResearchItems (REQUIRED)
    autoStartTimeMachine BOOLEAN, -- JSON: autoStartTimeMachine (REQUIRED)

    -- Raw storage
    file_size INTEGER,
    raw_json TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ARRAY TABLES (one table per root-level array)

-- transactions array -> transactions table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    transactionsItemId TEXT,  -- JSON: id
    day INTEGER,  -- JSON: day
    hour INTEGER,  -- JSON: hour
    minute INTEGER,  -- JSON: minute
    amount REAL,  -- JSON: amount
    label TEXT,  -- JSON: label
    balance REAL,  -- JSON: balance

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- loans array -> loans table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    provider TEXT,  -- JSON: provider
    daysLeft INTEGER,  -- JSON: daysLeft
    amountLeft INTEGER,  -- JSON: amountLeft
    active BOOLEAN,  -- JSON: active

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- candidates array -> candidates table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    candidatesItemId TEXT,  -- JSON: id
    name TEXT,  -- JSON: name
    originalName TEXT,  -- JSON: originalName
    employeeTypeName TEXT,  -- JSON: employeeTypeName
    salary INTEGER,  -- JSON: salary
    competitorProductId TEXT,  -- JSON: competitorProductId
    avatar TEXT,  -- JSON: avatar
    progress INTEGER,  -- JSON: progress
    level TEXT,  -- JSON: level
    employees TEXT,  -- JSON: employees
    speed INTEGER,  -- JSON: speed
    age INTEGER,  -- JSON: age
    maxSpeed INTEGER,  -- JSON: maxSpeed
    animationSpeed REAL,  -- JSON: animationSpeed
    requiredWer INTEGER,  -- JSON: requiredWer
    mood INTEGER,  -- JSON: mood
    overtimeMinutes INTEGER,  -- JSON: overtimeMinutes
    components TEXT,  -- JSON: components
    gender TEXT,  -- JSON: gender
    hoursLeft INTEGER,  -- JSON: hoursLeft
    callInSickDaysLeft INTEGER,  -- JSON: callInSickDaysLeft
    sickHoursLeft INTEGER,  -- JSON: sickHoursLeft
    idleMinutes INTEGER,  -- JSON: idleMinutes
    minutesTillNextEmotion INTEGER,  -- JSON: minutesTillNextEmotion
    creationTime INTEGER,  -- JSON: creationTime
    schedule TEXT,  -- JSON: schedule
    superstar BOOLEAN,  -- JSON: superstar
    leads TEXT,  -- JSON: leads
    leadFilters TEXT,  -- JSON: leadFilters
    task TEXT,  -- JSON: task
    demands TEXT,  -- JSON: demands
    researchDemands BOOLEAN,  -- JSON: researchDemands
    researchSalary BOOLEAN,  -- JSON: researchSalary

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- unassignedEmployees array -> unassignedEmployees table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS unassignedEmployees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- employeesOrder array -> employeesOrderList table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS employeesOrderList (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item value

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- activatedBenefits array -> activatedBenefits table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS activatedBenefits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item value

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- buildingHistory array -> buildingHistory table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS buildingHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    day INTEGER,  -- JSON: day
    buildingName TEXT,  -- JSON: buildingName

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- inventorySamples array -> inventorySamples table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS inventorySamples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- featureInstances array -> featureInstances table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS featureInstances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    featureInstancesItemId TEXT,  -- JSON: id
    featureName TEXT,  -- JSON: featureName
    activated BOOLEAN,  -- JSON: activated
    efficiency TEXT,  -- JSON: efficiency
    quality TEXT,  -- JSON: quality
    pricePerMonth INTEGER,  -- JSON: pricePerMonth
    premiumFeatures TEXT,  -- JSON: premiumFeatures
    productId TEXT,  -- JSON: productId
    requirements TEXT,  -- JSON: requirements
    dissatisfaction INTEGER,  -- JSON: dissatisfaction
    timeSlots TEXT,  -- JSON: timeSlots

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- contracts array -> contracts table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- products array -> products table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    productsItemId TEXT,  -- JSON: id
    name TEXT,  -- JSON: name
    ageInDays INTEGER,  -- JSON: ageInDays
    stats TEXT,  -- JSON: stats
    servers TEXT,  -- JSON: servers
    campaigns TEXT,  -- JSON: campaigns
    hostingAllocation INTEGER,  -- JSON: hostingAllocation
    frameworkName TEXT,  -- JSON: frameworkName
    investments TEXT,  -- JSON: investments
    mergers TEXT,  -- JSON: mergers
    supportTeams TEXT,  -- JSON: supportTeams
    tickets TEXT,  -- JSON: tickets
    ticketResolveTimes TEXT,  -- JSON: ticketResolveTimes
    resolvedTickets INTEGER,  -- JSON: resolvedTickets
    totalTickets INTEGER,  -- JSON: totalTickets
    ads TEXT,  -- JSON: ads
    nextDdosAttack INTEGER,  -- JSON: nextDdosAttack
    logoPath TEXT,  -- JSON: logoPath
    productTypeName TEXT,  -- JSON: productTypeName
    investor TEXT,  -- JSON: investor
    position INTEGER,  -- JSON: position
    ownedPercentage INTEGER,  -- JSON: ownedPercentage
    disableUserLoss BOOLEAN,  -- JSON: disableUserLoss
    lastDdosAttack INTEGER,  -- JSON: lastDdosAttack

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- marketingInsight array -> marketingInsight table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS marketingInsight (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- notifications array -> notifications table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- actions array -> actions table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- outsourcingTasks array -> outsourcingTasks table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS outsourcingTasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- productionPlans array -> productionPlans table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS productionPlans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    productionPlansItemId TEXT,  -- JSON: id
    name TEXT,  -- JSON: name
    production TEXT,  -- JSON: production
    skipModulesWithMissingRequirements BOOLEAN,  -- JSON: skipModulesWithMissingRequirements
    exceedTargets BOOLEAN,  -- JSON: exceedTargets

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- jeets array -> jeets table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS jeets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    jeetsItemId TEXT,  -- JSON: id
    gender TEXT,  -- JSON: gender
    name TEXT,  -- JSON: name
    handle TEXT,  -- JSON: handle
    avatar TEXT,  -- JSON: avatar
    text TEXT,  -- JSON: text
    day INTEGER,  -- JSON: day
    read BOOLEAN,  -- JSON: read

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- firedEmployees array -> firedEmployees table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS firedEmployees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    firedEmployeesItemId TEXT,  -- JSON: id
    name TEXT,  -- JSON: name
    originalName TEXT,  -- JSON: originalName
    employeeTypeName TEXT,  -- JSON: employeeTypeName
    salary INTEGER,  -- JSON: salary
    competitorProductId TEXT,  -- JSON: competitorProductId
    avatar TEXT,  -- JSON: avatar
    progress INTEGER,  -- JSON: progress
    level TEXT,  -- JSON: level
    employees TEXT,  -- JSON: employees
    speed REAL,  -- JSON: speed
    age INTEGER,  -- JSON: age
    maxSpeed INTEGER,  -- JSON: maxSpeed
    animationSpeed REAL,  -- JSON: animationSpeed
    requiredWer INTEGER,  -- JSON: requiredWer
    mood REAL,  -- JSON: mood
    overtimeMinutes INTEGER,  -- JSON: overtimeMinutes
    components TEXT,  -- JSON: components
    gender TEXT,  -- JSON: gender
    hoursLeft INTEGER,  -- JSON: hoursLeft
    callInSickDaysLeft INTEGER,  -- JSON: callInSickDaysLeft
    sickHoursLeft INTEGER,  -- JSON: sickHoursLeft
    idleMinutes INTEGER,  -- JSON: idleMinutes
    minutesTillNextEmotion INTEGER,  -- JSON: minutesTillNextEmotion
    creationTime INTEGER,  -- JSON: creationTime
    schedule TEXT,  -- JSON: schedule
    superstar BOOLEAN,  -- JSON: superstar
    queue TEXT,  -- JSON: queue
    demands TEXT,  -- JSON: demands
    researchDemands BOOLEAN,  -- JSON: researchDemands
    researchSalary BOOLEAN,  -- JSON: researchSalary
    negotiation TEXT,  -- JSON: negotiation
    hired DATETIME,  -- JSON: hired
    activeQueueIndex INTEGER,  -- JSON: activeQueueIndex
    task TEXT,  -- JSON: task
    lastTab TEXT,  -- JSON: lastTab
    lastEmotionName TEXT,  -- JSON: lastEmotionName
    lastBonusDay INTEGER,  -- JSON: lastBonusDay
    isTraining BOOLEAN,  -- JSON: isTraining
    lastDay INTEGER,  -- JSON: lastDay

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- resignedEmployees array -> resignedEmployees table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS resignedEmployees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    resignedEmployeesItemId TEXT,  -- JSON: id
    name TEXT,  -- JSON: name
    originalName TEXT,  -- JSON: originalName
    employeeTypeName TEXT,  -- JSON: employeeTypeName
    salary INTEGER,  -- JSON: salary
    competitorProductId TEXT,  -- JSON: competitorProductId
    avatar TEXT,  -- JSON: avatar
    progress INTEGER,  -- JSON: progress
    level TEXT,  -- JSON: level
    employees TEXT,  -- JSON: employees
    speed REAL,  -- JSON: speed
    age INTEGER,  -- JSON: age
    maxSpeed INTEGER,  -- JSON: maxSpeed
    animationSpeed REAL,  -- JSON: animationSpeed
    requiredWer INTEGER,  -- JSON: requiredWer
    mood REAL,  -- JSON: mood
    overtimeMinutes INTEGER,  -- JSON: overtimeMinutes
    components TEXT,  -- JSON: components
    gender TEXT,  -- JSON: gender
    hoursLeft INTEGER,  -- JSON: hoursLeft
    callInSickDaysLeft INTEGER,  -- JSON: callInSickDaysLeft
    sickHoursLeft INTEGER,  -- JSON: sickHoursLeft
    idleMinutes INTEGER,  -- JSON: idleMinutes
    minutesTillNextEmotion INTEGER,  -- JSON: minutesTillNextEmotion
    creationTime INTEGER,  -- JSON: creationTime
    schedule TEXT,  -- JSON: schedule
    superstar BOOLEAN,  -- JSON: superstar
    demands TEXT,  -- JSON: demands
    researchDemands BOOLEAN,  -- JSON: researchDemands
    researchSalary BOOLEAN,  -- JSON: researchSalary
    negotiation TEXT,  -- JSON: negotiation
    hired DATETIME,  -- JSON: hired
    lastTab TEXT,  -- JSON: lastTab
    task TEXT,  -- JSON: task
    lastSendHomeLength INTEGER,  -- JSON: lastSendHomeLength
    sendHomeDaysLeft INTEGER,  -- JSON: sendHomeDaysLeft
    isTraining BOOLEAN,  -- JSON: isTraining
    lastBonusDay INTEGER,  -- JSON: lastBonusDay
    lastEmotionName TEXT,  -- JSON: lastEmotionName
    lastCompetitorJobOffer INTEGER,  -- JSON: lastCompetitorJobOffer
    lastDay INTEGER,  -- JSON: lastDay

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- researchedItems array -> researchedItems table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS researchedItems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item value

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- competitorProducts array -> competitorProducts table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS competitorProducts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    -- Object fields
    competitorProductsItemId TEXT,  -- JSON: id
    name TEXT,  -- JSON: name
    logoColorDegree INTEGER,  -- JSON: logoColorDegree
    logoPath TEXT,  -- JSON: logoPath
    users REAL,  -- JSON: users
    productTypeName TEXT,  -- JSON: productTypeName
    controlled BOOLEAN,  -- JSON: controlled
    history TEXT,  -- JSON: history
    stockVolume INTEGER,  -- JSON: stockVolume
    ownedStocks INTEGER,  -- JSON: ownedStocks
    dealResults TEXT,  -- JSON: dealResults
    stockTransactions TEXT,  -- JSON: stockTransactions
    priceExpectations REAL,  -- JSON: priceExpectations
    growth INTEGER,  -- JSON: growth
    viralDaysLeft INTEGER,  -- JSON: viralDaysLeft
    version INTEGER,  -- JSON: version

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- loadedMods array -> loadedMods table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS loadedMods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),
    array_index INTEGER,  -- Position in original array

    value TEXT,  -- Array item (any type as JSON)

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id, array_index)
);

-- OBJECT TABLES (one table per root-level object)

-- progress object -> progress table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    products TEXT,  -- JSON: products

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- office object -> office table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS office (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    buildingName TEXT,  -- JSON: buildingName
    workstations TEXT,  -- JSON: workstations
    grid TEXT,  -- JSON: grid
    lastSelectedFloor TEXT,  -- JSON: lastSelectedFloor

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- completedEvents object -> completedEvents table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS completedEvents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    JeetInvestmentHint INTEGER,  -- JSON: JeetInvestmentHint
    EmployeeCallInSick INTEGER,  -- JSON: EmployeeCallInSick
    JeetTooMuchLevelDifference INTEGER,  -- JSON: JeetTooMuchLevelDifference
    ViralBoost INTEGER,  -- JSON: ViralBoost
    EmployeeCompetitorOffer INTEGER,  -- JSON: EmployeeCompetitorOffer
    DdosAttack INTEGER,  -- JSON: DdosAttack
    JeetHighResponseTime INTEGER,  -- JSON: JeetHighResponseTime

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- inventory object -> inventory table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    stats TEXT,  -- JSON: stats
    UiComponent INTEGER,  -- JSON: UiComponent
    BackendComponent INTEGER,  -- JSON: BackendComponent
    BlueprintComponent INTEGER,  -- JSON: BlueprintComponent
    GraphicsComponent INTEGER,  -- JSON: GraphicsComponent
    VideoComponent INTEGER,  -- JSON: VideoComponent
    UiElement INTEGER,  -- JSON: UiElement
    WireframeComponent INTEGER,  -- JSON: WireframeComponent
    InterfaceModule INTEGER,  -- JSON: InterfaceModule
    FrontendModule INTEGER,  -- JSON: FrontendModule
    NetworkComponent INTEGER,  -- JSON: NetworkComponent
    BackendModule INTEGER,  -- JSON: BackendModule
    VideoPlaybackModule INTEGER,  -- JSON: VideoPlaybackModule
    Copywriting INTEGER,  -- JSON: Copywriting
    TextFormat INTEGER,  -- JSON: TextFormat
    Firewall INTEGER,  -- JSON: Firewall
    OperatingSystem INTEGER,  -- JSON: OperatingSystem
    VirtualHardware INTEGER,  -- JSON: VirtualHardware
    ImageFormat INTEGER,  -- JSON: ImageFormat

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- purchaseInventory object -> purchaseInventory table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS purchaseInventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    glass_wall1 INTEGER,  -- JSON: glass_wall1
    glass_wall_corner1 INTEGER,  -- JSON: glass_wall_corner1
    glass_door2 INTEGER,  -- JSON: glass_door2

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- investmentProjects object -> investmentProjects table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS investmentProjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    SolarPower TEXT,  -- JSON: SolarPower

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- compatibilityModifiers object -> compatibilityModifiers table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS compatibilityModifiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),


    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- marketValues object -> marketValues table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS marketValues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    BlueprintComponent TEXT,  -- JSON: BlueprintComponent
    WireframeComponent TEXT,  -- JSON: WireframeComponent
    GraphicsComponent TEXT,  -- JSON: GraphicsComponent
    UiComponent TEXT,  -- JSON: UiComponent
    BackendComponent TEXT,  -- JSON: BackendComponent
    NetworkComponent TEXT,  -- JSON: NetworkComponent
    DatabaseComponent TEXT,  -- JSON: DatabaseComponent
    SemanticComponent TEXT,  -- JSON: SemanticComponent
    EncryptionComponent TEXT,  -- JSON: EncryptionComponent
    FilesystemComponent TEXT,  -- JSON: FilesystemComponent
    VideoComponent TEXT,  -- JSON: VideoComponent
    SmtpComponent TEXT,  -- JSON: SmtpComponent
    I18nComponent TEXT,  -- JSON: I18nComponent
    SearchAlgorithmComponent TEXT,  -- JSON: SearchAlgorithmComponent
    CompressionComponent TEXT,  -- JSON: CompressionComponent
    VirtualHardware TEXT,  -- JSON: VirtualHardware
    OperatingSystem TEXT,  -- JSON: OperatingSystem
    Firewall TEXT,  -- JSON: Firewall
    Copywriting TEXT,  -- JSON: Copywriting
    TextFormat TEXT,  -- JSON: TextFormat
    ImageFormat TEXT,  -- JSON: ImageFormat
    VideoFormat TEXT,  -- JSON: VideoFormat
    AudioFormat TEXT,  -- JSON: AudioFormat
    ContractAgreement TEXT,  -- JSON: ContractAgreement
    Survey TEXT,  -- JSON: Survey
    UserFeedback TEXT,  -- JSON: UserFeedback
    PhoneInterview TEXT,  -- JSON: PhoneInterview
    AnalyticsResearch TEXT,  -- JSON: AnalyticsResearch
    BehaviorObservation TEXT,  -- JSON: BehaviorObservation
    AbTesting TEXT,  -- JSON: AbTesting
    DocumentationComponent TEXT,  -- JSON: DocumentationComponent
    ProcessManagement TEXT,  -- JSON: ProcessManagement
    ContinuousIntegration TEXT,  -- JSON: ContinuousIntegration
    CronJob TEXT,  -- JSON: CronJob
    ResearchPoint TEXT,  -- JSON: ResearchPoint
    InterfaceModule TEXT,  -- JSON: InterfaceModule
    FrontendModule TEXT,  -- JSON: FrontendModule
    BackendModule TEXT,  -- JSON: BackendModule
    InputModule TEXT,  -- JSON: InputModule
    StorageModule TEXT,  -- JSON: StorageModule
    ContentManagementModule TEXT,  -- JSON: ContentManagementModule
    SeoModule TEXT,  -- JSON: SeoModule
    AuthenticationModule TEXT,  -- JSON: AuthenticationModule
    PaymentGatewayModule TEXT,  -- JSON: PaymentGatewayModule
    VideoPlaybackModule TEXT,  -- JSON: VideoPlaybackModule
    EmailModule TEXT,  -- JSON: EmailModule
    LocalizationModule TEXT,  -- JSON: LocalizationModule
    SearchModule TEXT,  -- JSON: SearchModule
    BandwidthCompressionModule TEXT,  -- JSON: BandwidthCompressionModule
    DatabaseLayer TEXT,  -- JSON: DatabaseLayer
    NotificationModule TEXT,  -- JSON: NotificationModule
    ApiClientModule TEXT,  -- JSON: ApiClientModule
    CodeOptimizationModule TEXT,  -- JSON: CodeOptimizationModule
    UiElement TEXT,  -- JSON: UiElement
    UiSet TEXT,  -- JSON: UiSet
    ResponsiveUi TEXT,  -- JSON: ResponsiveUi
    DesignGuidelines TEXT,  -- JSON: DesignGuidelines
    VirtualContainer TEXT,  -- JSON: VirtualContainer
    Cluster TEXT,  -- JSON: Cluster
    SwarmManagement TEXT,  -- JSON: SwarmManagement

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- variables object -> variables table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    ceoStartingAge INTEGER,  -- JSON: ceoStartingAge
    disableCeoAging BOOLEAN,  -- JSON: disableCeoAging
    disableEmployeeAging BOOLEAN,  -- JSON: disableEmployeeAging
    startingMoney INTEGER,  -- JSON: startingMoney
    everythingUnlocked BOOLEAN,  -- JSON: everythingUnlocked
    disableWorkstationLimit BOOLEAN,  -- JSON: disableWorkstationLimit
    disableInvestor BOOLEAN,  -- JSON: disableInvestor
    retirementAge INTEGER,  -- JSON: retirementAge
    daysPerYear INTEGER,  -- JSON: daysPerYear

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- ceo object -> ceo table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS ceo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    retirementFund TEXT,  -- JSON: retirementFund
    backstory TEXT,  -- JSON: backstory
    name TEXT,  -- JSON: name
    avatar TEXT,  -- JSON: avatar
    employeeId TEXT,  -- JSON: employeeId

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- employeesSortOrder object -> employeesSortOrderList table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS employeesSortOrderList (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    name TEXT,  -- JSON: name
    order BOOLEAN,  -- JSON: order

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- hosting object -> hosting table
-- ⭐ REQUIRED FIELD
CREATE TABLE IF NOT EXISTS hosting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_state_id INTEGER REFERENCES game_state(id),

    buildingName TEXT,  -- JSON: buildingName
    grid TEXT,  -- JSON: grid
    racks TEXT,  -- JSON: racks
    controllers TEXT,  -- JSON: controllers
    inventory TEXT,  -- JSON: inventory
    roomTemperature INTEGER,  -- JSON: roomTemperature
    performance TEXT,  -- JSON: performance

    -- Temporal tracking
    captured_at DATETIME,
    game_date TEXT,
    game_day INTEGER,

    UNIQUE(game_state_id)
);

-- PERFORMANCE INDEXES
CREATE INDEX IF NOT EXISTS idx_game_state_timestamp ON game_state(real_timestamp);
CREATE INDEX IF NOT EXISTS idx_game_state_date ON game_state(date);

CREATE INDEX IF NOT EXISTS idx_transactions_game_state ON transactions(game_state_id);
CREATE INDEX IF NOT EXISTS idx_transactions_captured_at ON transactions(captured_at);
CREATE INDEX IF NOT EXISTS idx_loans_game_state ON loans(game_state_id);
CREATE INDEX IF NOT EXISTS idx_loans_captured_at ON loans(captured_at);
CREATE INDEX IF NOT EXISTS idx_candidates_game_state ON candidates(game_state_id);
CREATE INDEX IF NOT EXISTS idx_candidates_captured_at ON candidates(captured_at);
CREATE INDEX IF NOT EXISTS idx_unassignedEmployees_game_state ON unassignedEmployees(game_state_id);
CREATE INDEX IF NOT EXISTS idx_unassignedEmployees_captured_at ON unassignedEmployees(captured_at);
CREATE INDEX IF NOT EXISTS idx_employeesOrderList_game_state ON employeesOrderList(game_state_id);
CREATE INDEX IF NOT EXISTS idx_employeesOrderList_captured_at ON employeesOrderList(captured_at);
CREATE INDEX IF NOT EXISTS idx_activatedBenefits_game_state ON activatedBenefits(game_state_id);
CREATE INDEX IF NOT EXISTS idx_activatedBenefits_captured_at ON activatedBenefits(captured_at);
CREATE INDEX IF NOT EXISTS idx_buildingHistory_game_state ON buildingHistory(game_state_id);
CREATE INDEX IF NOT EXISTS idx_buildingHistory_captured_at ON buildingHistory(captured_at);
CREATE INDEX IF NOT EXISTS idx_inventorySamples_game_state ON inventorySamples(game_state_id);
CREATE INDEX IF NOT EXISTS idx_inventorySamples_captured_at ON inventorySamples(captured_at);
CREATE INDEX IF NOT EXISTS idx_featureInstances_game_state ON featureInstances(game_state_id);
CREATE INDEX IF NOT EXISTS idx_featureInstances_captured_at ON featureInstances(captured_at);
CREATE INDEX IF NOT EXISTS idx_contracts_game_state ON contracts(game_state_id);
CREATE INDEX IF NOT EXISTS idx_contracts_captured_at ON contracts(captured_at);
CREATE INDEX IF NOT EXISTS idx_products_game_state ON products(game_state_id);
CREATE INDEX IF NOT EXISTS idx_products_captured_at ON products(captured_at);
CREATE INDEX IF NOT EXISTS idx_marketingInsight_game_state ON marketingInsight(game_state_id);
CREATE INDEX IF NOT EXISTS idx_marketingInsight_captured_at ON marketingInsight(captured_at);
CREATE INDEX IF NOT EXISTS idx_notifications_game_state ON notifications(game_state_id);
CREATE INDEX IF NOT EXISTS idx_notifications_captured_at ON notifications(captured_at);
CREATE INDEX IF NOT EXISTS idx_actions_game_state ON actions(game_state_id);
CREATE INDEX IF NOT EXISTS idx_actions_captured_at ON actions(captured_at);
CREATE INDEX IF NOT EXISTS idx_outsourcingTasks_game_state ON outsourcingTasks(game_state_id);
CREATE INDEX IF NOT EXISTS idx_outsourcingTasks_captured_at ON outsourcingTasks(captured_at);
CREATE INDEX IF NOT EXISTS idx_productionPlans_game_state ON productionPlans(game_state_id);
CREATE INDEX IF NOT EXISTS idx_productionPlans_captured_at ON productionPlans(captured_at);
CREATE INDEX IF NOT EXISTS idx_jeets_game_state ON jeets(game_state_id);
CREATE INDEX IF NOT EXISTS idx_jeets_captured_at ON jeets(captured_at);
CREATE INDEX IF NOT EXISTS idx_firedEmployees_game_state ON firedEmployees(game_state_id);
CREATE INDEX IF NOT EXISTS idx_firedEmployees_captured_at ON firedEmployees(captured_at);
CREATE INDEX IF NOT EXISTS idx_resignedEmployees_game_state ON resignedEmployees(game_state_id);
CREATE INDEX IF NOT EXISTS idx_resignedEmployees_captured_at ON resignedEmployees(captured_at);
CREATE INDEX IF NOT EXISTS idx_researchedItems_game_state ON researchedItems(game_state_id);
CREATE INDEX IF NOT EXISTS idx_researchedItems_captured_at ON researchedItems(captured_at);
CREATE INDEX IF NOT EXISTS idx_competitorProducts_game_state ON competitorProducts(game_state_id);
CREATE INDEX IF NOT EXISTS idx_competitorProducts_captured_at ON competitorProducts(captured_at);
CREATE INDEX IF NOT EXISTS idx_loadedMods_game_state ON loadedMods(game_state_id);
CREATE INDEX IF NOT EXISTS idx_loadedMods_captured_at ON loadedMods(captured_at);
CREATE INDEX IF NOT EXISTS idx_progress_game_state ON progress(game_state_id);
CREATE INDEX IF NOT EXISTS idx_office_game_state ON office(game_state_id);
CREATE INDEX IF NOT EXISTS idx_completedEvents_game_state ON completedEvents(game_state_id);
CREATE INDEX IF NOT EXISTS idx_inventory_game_state ON inventory(game_state_id);
CREATE INDEX IF NOT EXISTS idx_purchaseInventory_game_state ON purchaseInventory(game_state_id);
CREATE INDEX IF NOT EXISTS idx_investmentProjects_game_state ON investmentProjects(game_state_id);
CREATE INDEX IF NOT EXISTS idx_compatibilityModifiers_game_state ON compatibilityModifiers(game_state_id);
CREATE INDEX IF NOT EXISTS idx_marketValues_game_state ON marketValues(game_state_id);
CREATE INDEX IF NOT EXISTS idx_variables_game_state ON variables(game_state_id);
CREATE INDEX IF NOT EXISTS idx_ceo_game_state ON ceo(game_state_id);
CREATE INDEX IF NOT EXISTS idx_employeesSortOrderList_game_state ON employeesSortOrderList(game_state_id);
CREATE INDEX IF NOT EXISTS idx_hosting_game_state ON hosting(game_state_id);