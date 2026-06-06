"""
Real-world internship content for all 20 domains.
Used by the domain_detail route to pass structured content to the template.
"""

DOMAIN_CONTENT = {
    "Frontend Developer": {
        "icon": "fa-code",
        "color": "#3b82f6",
        "technologies": ["HTML5", "CSS3", "JavaScript", "React", "Angular", "Bootstrap"],
        "tasks": [
            "Design responsive web pages for various screen sizes",
            "Create landing pages and interactive dashboards",
            "Develop reusable UI components and design systems",
            "Implement navigation menus and multi-step forms",
            "Integrate frontend with REST APIs",
            "Optimize website performance and page load speed",
            "Fix UI bugs and improve user experience",
            "Create forms with client-side and server-side validation",
            "Develop portfolio and business websites",
            "Deploy frontend projects to hosting platforms",
        ],
        "outcomes": [
            ("fa-mobile-alt", "Responsive Design", "Build layouts that work on all devices"),
            ("fa-js", "Modern JavaScript", "Master ES6+, async/await, and DOM manipulation"),
            ("fa-react", "React/Angular Development", "Build component-based applications"),
            ("fa-plug", "API Integration", "Fetch and display live data from APIs"),
            ("fa-tachometer-alt", "UI Optimization", "Improve Core Web Vitals and load speed"),
        ],
    },

    "Backend Developer": {
        "icon": "fa-server",
        "color": "#10b981",
        "technologies": ["Node.js", "Python", "Java", "REST APIs", "SQL", "NoSQL"],
        "tasks": [
            "Develop and document REST APIs",
            "Create authentication and authorization systems",
            "Manage server-side business logic",
            "Handle database operations (CRUD)",
            "Build user management modules",
            "Implement role-based access control (RBAC)",
            "Secure APIs using JWT and OAuth",
            "Create payment gateway integrations",
            "Perform backend testing with unit and integration tests",
            "Deploy backend applications to cloud servers",
        ],
        "outcomes": [
            ("fa-cogs", "API Development", "Design and build scalable REST APIs"),
            ("fa-database", "Database Management", "Work with SQL and NoSQL databases"),
            ("fa-lock", "Authentication & Security", "Secure apps with JWT and OAuth2"),
            ("fa-cloud-upload-alt", "Server Deployment", "Deploy to AWS, Heroku, or VPS"),
        ],
    },

    "MEAN Stack Developer": {
        "icon": "fa-layer-group",
        "color": "#8b5cf6",
        "technologies": ["MongoDB", "Express.js", "Angular", "Node.js"],
        "tasks": [
            "Build complete full-stack web applications",
            "Design MongoDB databases and collections",
            "Create Angular user interfaces and components",
            "Develop backend APIs using Node.js and Express",
            "Implement authentication modules with JWT",
            "Connect Angular frontend with Node.js backend",
            "Perform full CRUD operations across the stack",
            "Test and debug applications end-to-end",
            "Deploy complete MEAN stack projects",
        ],
        "outcomes": [
            ("fa-layer-group", "Full Stack Development", "Build apps from database to UI"),
            ("fa-database", "Database Design", "Model data in MongoDB effectively"),
            ("fa-plug", "API Development", "Create and consume RESTful APIs"),
            ("fa-angular", "Angular Framework", "Build reactive SPAs with Angular"),
        ],
    },

    "Full Stack Developer": {
        "icon": "fa-laptop-code",
        "color": "#f59e0b",
        "technologies": ["HTML", "CSS", "JavaScript", "Node.js", "Python", "MySQL", "MongoDB"],
        "tasks": [
            "Develop complete web applications from scratch",
            "Create user registration and login systems",
            "Design and optimize database schemas",
            "Build admin dashboards and reporting modules",
            "Integrate third-party APIs and services",
            "Implement authentication and session management",
            "Deploy projects to cloud platforms (AWS, GCP)",
            "Optimize application performance",
            "Write technical project documentation",
        ],
        "outcomes": [
            ("fa-laptop-code", "End-to-End Development", "Own the full application lifecycle"),
            ("fa-database", "Database Integration", "Design and query relational/NoSQL DBs"),
            ("fa-rocket", "Deployment & Maintenance", "Ship and maintain production apps"),
        ],
    },

    "Cyber Security": {
        "icon": "fa-shield-alt",
        "color": "#ef4444",
        "technologies": ["Kali Linux", "Metasploit", "Wireshark", "Burp Suite", "Nmap"],
        "tasks": [
            "Conduct vulnerability assessments on web apps",
            "Perform comprehensive security audits",
            "Learn penetration testing techniques (OWASP Top 10)",
            "Analyze network traffic and identify anomalies",
            "Identify and exploit web application vulnerabilities",
            "Create detailed security audit reports",
            "Monitor and respond to security incidents",
            "Study malware behavior and reverse engineering",
            "Secure web applications against common attacks",
        ],
        "outcomes": [
            ("fa-user-secret", "Ethical Hacking", "Legally test systems for vulnerabilities"),
            ("fa-bug", "Vulnerability Analysis", "Identify and classify security risks"),
            ("fa-flask", "Security Testing", "Use industry-standard pen testing tools"),
            ("fa-clipboard-list", "Risk Assessment", "Document and prioritize security risks"),
        ],
    },

    "Data Science / ML / AI Intern": {
        "icon": "fa-brain",
        "color": "#6366f1",
        "technologies": ["Python", "TensorFlow", "Scikit-learn", "Pandas", "NLP", "OpenCV"],
        "tasks": [
            "Data collection, wrangling, and cleaning",
            "Data visualization with Matplotlib and Seaborn",
            "Machine learning model development and training",
            "Predictive analytics on real datasets",
            "Natural Language Processing (NLP) projects",
            "Image classification with CNNs",
            "Model evaluation, tuning, and validation",
            "AI chatbot development",
            "Build interactive analytics dashboards",
        ],
        "outcomes": [
            ("fa-chart-bar", "Data Analysis", "Extract insights from complex datasets"),
            ("fa-robot", "Machine Learning", "Train and deploy ML models"),
            ("fa-brain", "AI Development", "Build NLP and computer vision systems"),
            ("fa-cloud-upload-alt", "Model Deployment", "Serve models via APIs and dashboards"),
        ],
    },

    "App Developer": {
        "icon": "fa-mobile-alt",
        "color": "#14b8a6",
        "technologies": ["Flutter", "React Native", "Android (Java/Kotlin)", "iOS (Swift)", "Firebase"],
        "tasks": [
            "Develop mobile applications for Android and iOS",
            "Create responsive and intuitive mobile UI",
            "Integrate REST APIs into mobile apps",
            "Implement user authentication (Firebase, JWT)",
            "Integrate local and cloud database storage",
            "Set up push notification systems",
            "Test and debug apps on real and emulated devices",
            "Publish applications to Play Store / App Store",
            "Optimize app performance and battery usage",
        ],
        "outcomes": [
            ("fa-mobile-alt", "Mobile Development", "Build native and cross-platform apps"),
            ("fa-clone", "Cross-Platform Apps", "Write once, run on Android and iOS"),
            ("fa-plug", "API Integration", "Connect mobile apps to backend services"),
        ],
    },

    "Web Developer": {
        "icon": "fa-globe",
        "color": "#0ea5e9",
        "technologies": ["HTML5", "CSS3", "JavaScript", "Bootstrap", "Flask", "MySQL"],
        "tasks": [
            "Create fully responsive websites",
            "Develop dynamic web pages with JavaScript",
            "Build Flask web applications",
            "Integrate MySQL/SQLite databases",
            "Create and validate contact and registration forms",
            "Implement login and session management systems",
            "Deploy websites to hosting servers",
            "Perform website maintenance and updates",
        ],
        "outcomes": [
            ("fa-globe", "Website Development", "Build and deploy full websites"),
            ("fa-python", "Flask Framework", "Develop Python web applications"),
            ("fa-database", "Database Integration", "Connect web apps to databases"),
        ],
    },

    "UI/UX Designer": {
        "icon": "fa-paint-brush",
        "color": "#ec4899",
        "technologies": ["Figma", "Adobe XD", "Canva", "InVision", "Zeplin"],
        "tasks": [
            "Conduct user research and create user personas",
            "Create wireframes and low-fidelity prototypes",
            "Design high-fidelity interactive prototypes",
            "Design mobile app UI screens",
            "Design website UI and style guides",
            "Map user journeys and information architecture",
            "Conduct usability testing sessions",
            "Create and maintain design systems",
            "Present design concepts and gather feedback",
        ],
        "outcomes": [
            ("fa-palette", "UI Design", "Create beautiful, pixel-perfect interfaces"),
            ("fa-search", "UX Research", "Understand and advocate for users"),
            ("fa-object-group", "Prototyping", "Build interactive design prototypes"),
            ("fa-users", "User-Centered Design", "Design solutions that solve real problems"),
        ],
    },

    "Technical Support": {
        "icon": "fa-headset",
        "color": "#64748b",
        "technologies": ["Windows Server", "Linux", "Networking", "Ticketing Systems", "Remote Tools"],
        "tasks": [
            "Diagnose and resolve hardware and software issues",
            "Provide software installation and configuration support",
            "Manage user accounts and access permissions",
            "Monitor system health and performance",
            "Troubleshoot network connectivity issues",
            "Handle and resolve support tickets in SLA",
            "Create technical documentation and SOPs",
            "Assist customers with technical queries",
        ],
        "outcomes": [
            ("fa-tools", "IT Support Skills", "Solve real technical problems confidently"),
            ("fa-search-plus", "Troubleshooting", "Systematically diagnose and fix issues"),
            ("fa-server", "System Administration", "Manage users, servers, and networks"),
        ],
    },

    "Business Development Associate": {
        "icon": "fa-handshake",
        "color": "#f97316",
        "technologies": ["CRM Tools", "MS Excel", "PowerPoint", "LinkedIn", "Salesforce"],
        "tasks": [
            "Identify and qualify new business leads",
            "Conduct market research and competitor analysis",
            "Communicate with potential clients via email and calls",
            "Prepare weekly and monthly sales reports",
            "Create business proposals and presentations",
            "Maintain customer relationships using CRM",
            "Develop partnership and collaboration strategies",
            "Analyze revenue growth and conversion rates",
        ],
        "outcomes": [
            ("fa-chess", "Business Strategy", "Develop strategies for business growth"),
            ("fa-phone", "Sales Skills", "Learn B2B and B2C sales techniques"),
            ("fa-user-tie", "Client Management", "Build and maintain client relationships"),
        ],
    },

    "Human Resources (HR)": {
        "icon": "fa-users",
        "color": "#84cc16",
        "technologies": ["HR Software", "MS Excel", "ATS Systems", "LinkedIn", "Zoom"],
        "tasks": [
            "Screen resumes and shortlist candidates",
            "Source candidates via job portals and LinkedIn",
            "Schedule and coordinate interviews",
            "Assist with employee onboarding processes",
            "Maintain HR documentation and employee records",
            "Track and manage attendance records",
            "Run recruitment campaigns on social media",
            "Plan and execute employee engagement activities",
        ],
        "outcomes": [
            ("fa-search", "Recruitment Process", "Master end-to-end hiring workflows"),
            ("fa-clipboard-list", "HR Operations", "Handle daily HR administration tasks"),
            ("fa-users", "Employee Management", "Support employee lifecycle activities"),
        ],
    },

    "Marketing": {
        "icon": "fa-bullhorn",
        "color": "#f43f5e",
        "technologies": ["Google Analytics", "Canva", "Mailchimp", "HubSpot", "SEMrush"],
        "tasks": [
            "Conduct market and consumer research",
            "Perform brand analysis and positioning",
            "Plan and execute marketing campaigns",
            "Analyze competitor strategies and positioning",
            "Create and distribute customer surveys",
            "Prepare marketing performance reports",
            "Develop creative promotional strategies",
        ],
        "outcomes": [
            ("fa-chart-line", "Marketing Strategy", "Plan data-driven marketing campaigns"),
            ("fa-star", "Branding", "Build strong brand identity and messaging"),
            ("fa-chart-bar", "Market Analysis", "Interpret data to find opportunities"),
        ],
    },

    "Digital Content Creator": {
        "icon": "fa-photo-video",
        "color": "#a855f7",
        "technologies": ["Canva", "Adobe Premiere", "After Effects", "Instagram", "YouTube Studio"],
        "tasks": [
            "Create engaging social media content (reels, posts)",
            "Design graphics and promotional banners",
            "Edit and produce short-form videos",
            "Schedule content using social media tools",
            "Develop creative campaign ideas",
            "Design eye-catching thumbnails and posters",
            "Optimize content for platform algorithms",
        ],
        "outcomes": [
            ("fa-photo-video", "Content Creation", "Produce high-quality digital content"),
            ("fa-film", "Video Editing", "Edit and produce professional videos"),
            ("fa-palette", "Graphic Design", "Design visuals that drive engagement"),
        ],
    },

    "Social Media Promotion": {
        "icon": "fa-share-alt",
        "color": "#06b6d4",
        "technologies": ["Instagram", "Facebook", "LinkedIn", "Twitter/X", "Hootsuite", "Buffer"],
        "tasks": [
            "Manage brand social media accounts daily",
            "Create promotional posts and stories",
            "Schedule and publish content consistently",
            "Engage with audience comments and messages",
            "Research trending hashtags and topics",
            "Analyze page performance and audience insights",
            "Plan and execute social media campaigns",
        ],
        "outcomes": [
            ("fa-hashtag", "Social Media Marketing", "Grow brands on major platforms"),
            ("fa-users", "Community Building", "Build and engage loyal online communities"),
            ("fa-chart-bar", "Analytics", "Track KPIs and optimize social strategy"),
        ],
    },

    "Digital Marketing": {
        "icon": "fa-chart-line",
        "color": "#22c55e",
        "technologies": ["Google Ads", "Facebook Ads", "SEMrush", "Google Analytics", "Ahrefs"],
        "tasks": [
            "Implement on-page and off-page SEO strategies",
            "Create and manage Google Ads campaigns",
            "Run social media paid advertising",
            "Perform keyword research and analysis",
            "Analyze website traffic with Google Analytics",
            "Execute lead generation campaigns",
            "Prepare performance and ROI reports",
        ],
        "outcomes": [
            ("fa-search", "SEO", "Rank websites higher on search engines"),
            ("fa-google", "SEM", "Run profitable paid search campaigns"),
            ("fa-ad", "Digital Advertising", "Manage multi-channel ad campaigns"),
        ],
    },

    "SMS / Email Marketing": {
        "icon": "fa-envelope-open-text",
        "color": "#eab308",
        "technologies": ["Mailchimp", "SendGrid", "Klaviyo", "HubSpot", "Twilio"],
        "tasks": [
            "Design visually engaging email campaigns",
            "Write compelling newsletters and drip sequences",
            "Segment audiences for targeted messaging",
            "Set up marketing automation workflows",
            "Track email open rates, CTR, and conversions",
            "Manage and execute SMS marketing campaigns",
            "Conduct A/B testing on subject lines and CTAs",
        ],
        "outcomes": [
            ("fa-envelope", "Email Marketing", "Design campaigns that convert"),
            ("fa-robot", "Campaign Automation", "Build automated marketing funnels"),
            ("fa-users-cog", "Audience Targeting", "Deliver the right message to the right person"),
        ],
    },

    "Process Associate": {
        "icon": "fa-tasks",
        "color": "#78716c",
        "technologies": ["MS Excel", "MS Word", "ERP Systems", "Google Sheets", "Slack"],
        "tasks": [
            "Create and maintain process documentation",
            "Identify and implement workflow optimizations",
            "Perform data entry, cleaning, and analysis",
            "Prepare operational and management reports",
            "Conduct quality checks on deliverables",
            "Provide day-to-day operational support",
            "Lead process improvement initiatives",
        ],
        "outcomes": [
            ("fa-cogs", "Operations Management", "Streamline business processes"),
            ("fa-sync", "Process Optimization", "Reduce waste and increase efficiency"),
            ("fa-file-alt", "Business Reporting", "Communicate insights through data"),
        ],
    },

    "Short Film Maker / Ads Creator": {
        "icon": "fa-video",
        "color": "#f472b6",
        "technologies": ["Adobe Premiere Pro", "DaVinci Resolve", "After Effects", "Final Cut Pro"],
        "tasks": [
            "Write scripts and screenplays for videos",
            "Create storyboards and shot lists",
            "Plan and execute video shoots",
            "Edit footage using professional tools",
            "Produce compelling advertisements",
            "Create promotional and awareness videos",
            "Synchronize audio, SFX, and music",
            "Direct creative vision end-to-end",
        ],
        "outcomes": [
            ("fa-film", "Film Production", "Manage productions from concept to delivery"),
            ("fa-book-open", "Storytelling", "Craft narratives that engage audiences"),
            ("fa-cut", "Video Editing", "Edit professionally with industry tools"),
        ],
    },

    "Content Writer": {
        "icon": "fa-pen-nib",
        "color": "#64748b",
        "technologies": ["WordPress", "Grammarly", "SEMrush", "Google Docs", "Surfer SEO"],
        "tasks": [
            "Write high-quality blog posts on assigned topics",
            "Create in-depth articles and thought leadership pieces",
            "Write website copy (home, about, service pages)",
            "Produce SEO-optimized content targeting keywords",
            "Write product and service descriptions",
            "Create technical documentation and user guides",
            "Write engaging social media captions",
            "Proofread and edit content for quality",
        ],
        "outcomes": [
            ("fa-pen", "Content Writing", "Write clear, engaging, and impactful content"),
            ("fa-search", "SEO Writing", "Optimize content for search engine rankings"),
            ("fa-bullhorn", "Copywriting", "Write persuasive copy that drives action"),
        ],
    },
}


def get_domain_content(domain_name):
    """Returns content dict for a domain, or a generic fallback."""
    # Try exact match first
    if domain_name in DOMAIN_CONTENT:
        return DOMAIN_CONTENT[domain_name]
    # Try case-insensitive match
    for key, val in DOMAIN_CONTENT.items():
        if key.lower() == domain_name.lower():
            return val
    # Return generic fallback
    return {
        "icon": "fa-briefcase",
        "color": "#0a2463",
        "technologies": ["Industry Tools", "Professional Software"],
        "tasks": [
            "Work on assigned real-world projects",
            "Attend mentorship sessions and workshops",
            "Submit weekly progress reports",
            "Collaborate with team members",
            "Complete final project and documentation",
        ],
        "outcomes": [
            ("fa-briefcase", "Professional Skills", "Develop industry-relevant expertise"),
            ("fa-certificate", "Certification", "Earn a recognized completion certificate"),
        ],
    }
