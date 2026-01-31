import React, { useState, useMemo, memo } from 'react';
import {
    HelpCircle, Shield, Database, Target, Brain, Radar,
    BarChart2, Zap, Layers, Search
} from 'lucide-react';
import { StarsCanvas } from '../components/ui/StarsCanvas';
import VaporizeTextCycle, { Tag } from '../components/ui/VaporizeTextCycle';
import FlipCard from '../components/ui/FlipCard';

// Memoized Header to prevent re-renders causing animation glitches
const HeaderSection = memo(() => (
    <header className="text-center space-y-4 mb-12 flex flex-col items-center w-full">
        <div className="h-[100px] w-full flex justify-center items-center">
            <VaporizeTextCycle
                texts={["System Architecture", "Core Concepts", "Security Protocols"]}
                font={{ fontFamily: "Inter, sans-serif", fontSize: "60px", fontWeight: 700 }}
                color="rgba(192, 132, 252, 1)"
                spread={5} density={8}
                animation={{ vaporizeDuration: 1.5, fadeInDuration: 0.8, waitDuration: 2.5 }}
                direction="left-to-right" alignment="center" tag={Tag.H1}
            />
        </div>
    </header>
));

const QAPage = () => {
    // State
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('All');

    // Data with Hex Colors for FlipCard
    const qaGroups = [
        {
            title: "Clean Data",
            id: "clean-data",
            icon: Database,
            color: "#3b82f6", // blue-500
            description: "Reduces manual scanner fatigue by enriching raw text with structural context.",
            items: [
                {
                    id: "clean-1",
                    q: "What is the criterion for 'Clean' data?",
                    a: "Clean data is 'Contextual, Syntax-Validated Code Blocks.' Example Metadata: { language: 'Python', confidence: 0.94 (AST), source: 'repo/path/file.py:120-168', tags: ['secret', 'injection-risk'] }.",
                    features: ["Contextual", "Syntax-Validated", "Structured JSON"]
                },
                {
                    id: "clean-2",
                    q: "What is considered 'Noise'?",
                    a: "Noise includes narrative prose, junk code (broken snippets), build artifacts (node_modules, vendor folders), and minified/obfuscated code that holds little analytical value.",
                    features: ["Narrative Prose", "Build Artifacts", "Minified Code"]
                },
                {
                    id: "clean-3",
                    q: "What is the output format?",
                    a: "We offer JSON for API integrations, UI Cards for visual inspection, and basic CSV export options. Richer JSON schema & PDF reports are planned for v3.0.",
                    features: ["JSON API", "UI Cards", "CSV Export"]
                }
            ]
        },
        {
            title: "Usage Scenarios",
            id: "usage",
            icon: Target,
            color: "#22c55e", // green-500
            description: "Aligns with real-world DevSecOps workflows vs generic search.",
            items: [
                {
                    id: "use-1",
                    q: "Most common target: Document or Repo?",
                    a: "Approximately 70% Git Repositories (the primary surface for modern DevSecOps) and 30% Documents (legacy systems, technical specs, security reports).",
                    features: ["Git Repos (70%)", "Documents (30%)", "DevSecOps"]
                },
                {
                    id: "use-2",
                    q: "What are users looking for in 'Critical SQL' examples?",
                    a: "Users typically search for (c) Vulnerability Traces (e.g., user input in SQL strings indicating Injection risks) and (a) Specific Patterns (e.g., database schema definitions or sensitive data queries).",
                    features: ["Vuln Traces", "Schema Defs", "Injection Risks"]
                },
                {
                    id: "use-3",
                    q: "Top 3 Security Search Types?",
                    a: "1. Hardcoded Secrets (API Keys, passwords). 2. Injection Patterns (SQLi, XSS). 3. Dangerous Functions (RCE risks like os.system).",
                    features: ["Secrets", "Injection (SQLi/XSS)", "RCE Risks"]
                }
            ]
        },
        {
            title: "Accuracy & Metrics",
            id: "metrics",
            icon: Radar,
            color: "#ef4444", // red-500
            description: "Trust is built on precision; false alarms kill adoption.",
            items: [
                {
                    id: "metric-1",
                    q: "'False Positive = 0' target scope?",
                    a: "We claim 'Near-zero false positives' specifically for **AST-validated code** (supported languages). If Tree-sitter validates the syntax, it is structurally confirmed as code. For unsupported languages, we use confidence-labeled fallbacks.",
                    features: ["AST-Validated", "Near-Zero FP", "Structurally Confirmed"]
                },
                {
                    id: "metric-2",
                    q: "False Negative vs False Positive tolerance?",
                    a: "We prioritize Precision over Recall. We'd rather miss one item than flood the user with 100 false alarms (Alert Fatigue), except for Secrets detection where we prioritize finding everything.",
                    features: ["Precision > Recall", "No Alert Fatigue", "Secrets Priority"]
                },
                {
                    id: "metric-3",
                    q: "Success Metrics?",
                    a: "Precision (Target 99+%), Time-to-Insight (< 60s for typical repositories), and Noise Reduction Rate (High ratio of raw input size to refined output size).",
                    features: ["99%+ Precision", "<60s Insight", "High Noise Reduction"]
                }
            ]
        },
        {
            title: "AST Layers",
            id: "ast",
            icon: Brain,
            color: "#eab308", // yellow-500
            description: "AST powered by Tree-sitter ensures structural understanding beyond Regex.",
            items: [
                {
                    id: "ast-1",
                    q: "Where does AST distinction happen?",
                    a: "Two layers: 1. **Document Segmentation**: Distinguishing code blocks from narrative prose in PDFs/TXT. 2. **Repo File Validation**: Parsing .py/.js files to extract specific structures (functions/classes) rather than just text.",
                    features: ["Doc Segmentation", "Repo Validation", "Structure Extraction"]
                },
                {
                    id: "ast-2",
                    q: "What if AST fails?",
                    a: "Tiered Strategy: Plan A is AST (High Confidence). Plan B is Regex Fallback (Medium Confidence, with UI warning). Plan C is Reject (to preserve signal against noise).",
                    features: ["Plan A: AST", "Plan B: Regex", "Plan C: Reject"]
                },
                {
                    id: "ast-3",
                    q: "How is Polyglot Language Detection handled?",
                    a: "Weighted Voting System: 1. File Extension (Most reliable). 2. Shebang (#!/bin/bash). 3. Heuristic Content Analysis (Looking for keywords like def, function, class).",
                    features: ["Weighted Voting", "File Extension", "Heuristics"]
                }
            ]
        },
        {
            title: "Security Lab",
            id: "security",
            icon: Shield,
            color: "#f97316", // orange-500
            description: "Zero-trust architecture allows safe analysis of potentially malicious code.",
            items: [
                {
                    id: "sec-1",
                    q: "How is isolation achieved?",
                    a: "Currently via Containerization with strict limits: **No execution permission**, no privileged containers, and strict resource limits (CPU/memory/time). We use **Read-only mounts** and per-session temp volumes that are securely wiped immediately after analysis.",
                    features: ["Containerized", "No-Exec Policy", "Ephemeral Volumes"]
                },
                {
                    id: "sec-2",
                    q: "Threat Model & Controls?",
                    a: "Static Analysis (we read, don't execute). No-exec policy: files are treated as data; nothing is executed. Repo Bloat: Size limits. Path Traversal: Filename sanitization.",
                    features: ["Static Analysis", "Read-Only", "Path Sanitization"]
                },
                {
                    id: "sec-3",
                    q: "Network Access & Git Clone?",
                    a: "We never execute untrusted code. Network is restricted; we perform **Static Manifest Parsing** (e.g., package.json) to analyze dependencies without fetching or installing them from the internet.",
                    features: ["Air-Gapped Analysis", "Static Parsing", "No Fetching"]
                },
                {
                    id: "sec-4",
                    q: "File System Permissions?",
                    a: "Read-Only application mount. Write access only in unique, short-lived /tmp session directories that are securely wiped after analysis.",
                    features: ["Read-Only Mount", "Secure Wipe", "Temp Isolation"]
                }
            ]
        },
        {
            title: "Analytics",
            id: "analytics",
            icon: BarChart2,
            color: "#6366f1", // indigo-500
            description: "from-indigo-500/10 to-transparent",
            items: [
                {
                    id: "ana-1",
                    q: "How is Language Distribution calculated?",
                    a: "Currently File Count based. Future update (v2.2) will move to LOC (Lines of Code) for higher accuracy.",
                    features: ["File Count", "LOC (Coming Soon)", "High Accuracy"]
                },
                {
                    id: "ana-2",
                    q: "What is the 'Complexity' metric?",
                    a: "Currently Indentation/Nesting heuristic (fast proxy metric in v2.0). Future update will implement Cyclomatic Complexity (counting conditional branches) for a scientific 'maintainability' score.",
                    features: ["Nesting Heuristic", "Cyclomatic Complexity", "Maintainability"]
                },
                {
                    id: "ana-3",
                    q: "Is the output strategic?",
                    a: "Yes. Confidence Scores alert users to 'Spaghetti Code' risks (high regex dependency). We inform strategy (Risk/Technical Debt), not just dump data.",
                    features: ["Confidence Scores", "Risk Alerts", "Tech Debt Info"]
                }
            ]
        },
        {
            title: "Product Flow",
            id: "product",
            icon: Layers,
            color: "#14b8a6", // teal-500
            description: "from-teal-500/10 to-transparent",
            items: [
                {
                    id: "prod-1",
                    q: "How do users use SENTINEL?",
                    a: "Web UI (Dashboard) for visualization. Enterprise version will add CLI for CI/CD pipelines.",
                    features: ["Web UI", "CLI (Enterprise)", "CI/CD Ready"]
                },
                {
                    id: "prod-2",
                    q: "Minimum Input?",
                    a: "Drag-and-drop file OR Git Repo URL. The system auto-discovers the rest.",
                    features: ["Drag-and-Drop", "Git URL", "Auto-Discovery"]
                },
                {
                    id: "prod-3",
                    q: "Data presentation?",
                    a: "Interactive Filtering Set. It's a 'Living Dataset' users can filter (e.g., 'Show me only Python with >90% confidence') rather than a static PDF.",
                    features: ["Interactive Filters", "Living Dataset", "Dynamic View"]
                }
            ]
        },
        {
            title: "Status v2/v3",
            id: "status",
            icon: Zap,
            color: "#06b6d4", // cyan-500
            description: "from-cyan-500/10 to-transparent",
            items: [
                {
                    id: "stat-1",
                    q: "What 5 features are 'Done' in v2?",
                    a: "1. Hybrid Extraction (AST+Regex). 2. Git Repo Analysis. 3. Polyglot Support (15+ langs). 4. Visual Dashboard. 5. Secure Input Handling (SSRF/XSS protection).",
                    features: ["Hybrid Extraction", "Git & Polyglot", "Secure Input"]
                },
                {
                    id: "stat-2",
                    q: "What 3 things are still 'Risky/Beta'?",
                    a: "1. Mobile UX (Terminal/Table spacing). 2. Massive Repos (>1GB memory management). 3. Advanced Export (Basic CSV is available; full JSON/PDF reports are in development).",
                    features: ["Mobile UX Beta", "Large Repo Handling", "Advanced Export"]
                },
                {
                    id: "stat-3",
                    q: "The single biggest move for v3?",
                    a: "ENTERPRISE INTEGRATION. Connecting findings directly to work management systems (e.g., 'Create Jira Ticket' or 'Open GitHub Issue' from a SENTINEL finding).",
                    features: ["Jira Integration", "GitHub Issues", "Workflow Automation"]
                }
            ]
        },
        {
            title: "Differentiation",
            id: "diff",
            icon: HelpCircle,
            color: "#a855f7", // purple-500
            description: "from-purple-500/10 to-transparent",
            items: [
                {
                    id: "diff-1",
                    q: "What tools do users use today?",
                    a: "Simple search (ripgrep/grep), Complex SAST (CodeQL/SonarQube/TruffleHog), or Platform-specific tools (GitHub Advanced Security).",
                    features: ["vs Ripgrep", "vs CodeQL", "vs GHAS"]
                },
                {
                    id: "diff-2",
                    q: "What is SENTINEL's clear difference?",
                    a: "Code Extraction from Documents. Unlike standard SAST tools that only scan source code files, SENTINEL intelligently extracts, parses, and validates code buried inside unstructured PDF, Word, and Text documents. This unlocks security review for legacy and compliance-heavy environments.",
                    features: ["Doc Extraction", "Unstructured Data", "Legacy Support"]
                }
            ]
        }
    ];

    // Filter Logic
    const filteredQuestions = useMemo(() => {
        let results = [];
        // Flatten all questions with category info
        qaGroups.forEach(group => {
            if (selectedCategory !== 'All' && group.title !== selectedCategory) return;
            group.items.forEach(item => {
                if (
                    searchQuery === '' ||
                    item.q.toLowerCase().includes(searchQuery.toLowerCase()) ||
                    item.a.toLowerCase().includes(searchQuery.toLowerCase())
                ) {
                    results.push({
                        ...item,
                        category: group.title,
                        icon: group.icon,
                        color: group.color
                    });
                }
            });
        });
        return results;
    }, [searchQuery, selectedCategory]);

    // Components
    const CategoryPill = ({ label, active, onClick }) => (
        <button
            onClick={onClick}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all duration-300 border backdrop-blur-md whitespace-nowrap
            ${active
                    ? 'bg-white text-black border-white shadow-[0_0_20px_rgba(255,255,255,0.3)] scale-105'
                    : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10 hover:text-white'}`}
        >
            {label}
        </button>
    );

    return (
        <div className="min-h-screen relative overflow-hidden text-white pb-32">
            <StarsCanvas speedMultiplier={0.05} brightness={0.8} />

            <div className="max-w-7xl mx-auto px-6 pt-12 relative z-10 flex flex-col items-center">

                {/* Isolated Header */}
                <HeaderSection />

                {/* Search & Filters */}
                <div className="w-full max-w-4xl space-y-8 mb-16">
                    {/* Search Input */}
                    <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-blue-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-500 opacity-50" />
                        <div className="relative bg-[#0f111a]/80 backdrop-blur-xl border border-white/10 rounded-2xl p-2 flex items-center shadow-2xl transition-all duration-300 group-hover:border-purple-500/30">
                            <Search className="text-gray-400 ml-4" size={24} />
                            <input
                                type="text"
                                placeholder="Search questions, keywords, or topics..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-transparent border-none text-white text-lg px-4 py-3 focus:outline-none placeholder:text-gray-500"
                            />
                        </div>
                    </div>

                    {/* Category Filter Pills */}
                    <div className="flex flex-wrap justify-center gap-3">
                        <CategoryPill
                            label="All"
                            active={selectedCategory === 'All'}
                            onClick={() => setSelectedCategory('All')}
                        />
                        {qaGroups.map(g => (
                            <CategoryPill
                                key={g.title}
                                label={g.title}
                                active={selectedCategory === g.title}
                                onClick={() => setSelectedCategory(g.title)}
                            />
                        ))}
                    </div>
                </div>

                {/* Flip Cards Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full max-w-7xl animate-fade-in-up">
                    {filteredQuestions.map((item) => (
                        <div key={item.id} className="flex justify-center">
                            <FlipCard
                                title={item.q}
                                subtitle={item.category}
                                description={item.a}
                                features={item.features}
                                color={item.color}
                                icon={item.icon}
                            />
                        </div>
                    ))}
                </div>

                {/* Empty State */}
                {filteredQuestions.length === 0 && (
                    <div className="text-center py-20 animate-fade-in-up">
                        <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Search size={32} className="text-gray-500" />
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-2">No results found</h3>
                        <p className="text-gray-400">Try adjusting your search terms or filters.</p>
                        <button
                            onClick={() => { setSearchQuery(''); setSelectedCategory('All'); }}
                            className="mt-6 px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors"
                        >
                            Reset filters
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default QAPage;
