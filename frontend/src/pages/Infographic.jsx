import React, { useState, useEffect, useRef } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement, Filler } from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import Plot from 'react-plotly.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  Filler
);

const Infographic = () => {
    const [activeTab, setActiveTab] = useState('infra');
    
    // Simulation state
    const [simModel, setSimModel] = useState(8);
    const [simTokens, setSimTokens] = useState(100);
    const [simNodes, setSimNodes] = useState(1);
    const [simResults, setSimResults] = useState({
        time: 0,
        vram: 0,
        efficiency: 0,
        tier: ''
    });

    const [simChartData, setSimChartData] = useState({
        labels: [],
        datasets: []
    });

    // --- DATA: Top 20 Models ---
    const topModels = [
        { name: "Llama-3-70B", params: "70B", ctx: "8k-128k", vram: "140GB+", pros: "SOTA performance, massive community support", cons: "High VRAM requirements for training" },
        { name: "Llama-3-8B", params: "8B", ctx: "8k", vram: "16GB+", pros: "Extremely fast, ideal for edge fine-tuning", cons: "Limited reasoning vs 70B" },
        { name: "Mistral-v0.3", params: "7.3B", ctx: "32k", vram: "16GB", pros: "Best-in-class 7B model, sliding window attn", cons: "Context window handling can be tricky" },
        { name: "Mixtral-8x7B", params: "46.7B", ctx: "32k", vram: "90GB+", pros: "MoE architecture, fast inference", cons: "Complex fine-tuning setup" },
        { name: "Phi-3-Mini", params: "3.8B", ctx: "128k", vram: "8GB", pros: "Microsoft optimized, high reasoning for size", cons: "Smaller knowledge base" },
        { name: "Qwen-2-72B", params: "72B", ctx: "128k", vram: "145GB+", pros: "Superior coding & math capabilities", cons: "High compute cost" },
        { name: "Gemma-2-27B", params: "27B", ctx: "8k", vram: "54GB+", pros: "Google specialized architecture, high safety", cons: "Restricted context window" },
        { name: "Grok-1", params: "314B", ctx: "n/a", vram: "600GB+", pros: "Massive raw knowledge, MoE architecture", cons: "Requires multi-node H100 setup" },
        { name: "DeepSeek-V2", params: "236B", ctx: "128k", vram: "500GB+", pros: "Excellent MoE scaling, code-focused", cons: "Complex infrastructure needed" },
        { name: "StarCoder2-15B", params: "15B", ctx: "16k", vram: "32GB+", pros: "The gold standard for code fine-tuning", cons: "Weak at general natural language" },
        { name: "Yi-1.5-34B", params: "34B", ctx: "200k", vram: "70GB+", pros: "Long context master, strong bilingual", cons: "Specific prompt template sensitivity" },
        { name: "Falcon-180B", params: "180B", ctx: "2k", vram: "360GB+", pros: "Massive data density, raw power", cons: "Legacy context window, massive VRAM" },
        { name: "Command R+", params: "104B", ctx: "128k", vram: "200GB+", pros: "Optimized for RAG and Tool Use", cons: "Large VRAM footprint" },
        { name: "DBRX", params: "132B", ctx: "32k", vram: "260GB+", pros: "Databricks MoE, high efficiency", cons: "Heavy compute requirements" },
        { name: "OLMo-7B", params: "7B", ctx: "2k", vram: "15GB", pros: "Fully open weights & data artifacts", cons: "Early research stage" },
        { name: "Pythia-12B", params: "12B", ctx: "2k", vram: "24GB", pros: "Excellent for interpretability research", cons: "Lower benchmark scores" },
        { name: "MPT-30B", params: "30B", ctx: "8k", vram: "60GB", pros: "MosaicML optimized, very stable", cons: "Context window is dated" },
        { name: "StableLM-2", params: "12B", ctx: "4k", vram: "24GB", pros: "Stable Diffusion creators, creative bias", cons: "Limited logic tasks" },
        { name: "Granite-20B", params: "20B", ctx: "8k", vram: "40GB", pros: "IBM enterprise grade, legal safety", cons: "Conservative output" },
        { name: "Bloom-176B", params: "176B", ctx: "2k", vram: "350GB+", pros: "Massive multi-lingual dataset", cons: "Inference latency is high" }
    ];

    // --- Utility: Label Wrapper ---
    const wrapLabel = (label) => {
        if (typeof label !== 'string' || label.length <= 16) return label;
        const words = label.split(' ');
        let lines = [], current = "";
        words.forEach(w => {
            if ((current + w).length > 16) { lines.push(current.trim()); current = w + " "; }
            else { current += w + " "; }
        });
        lines.push(current.trim());
        return lines;
    };

    // --- Chart Data: Infrastructure ---
    const infraData = {
        labels: ['CPU Core Count', 'GPU Memory (GB)', 'Storage (TB)', 'RAM Pool (TB)'].map(wrapLabel),
        datasets: [{
            label: 'Available Resources',
            data: [2240, 1280, 400, 16],
            backgroundColor: ['#0ea5e9', '#a855f7', '#f472b6', '#10b981'],
            borderRadius: 8
        }]
    };

    const infraOptions = {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b' } },
            y: { ticks: { color: '#f1f5f9' } }
        }
    };

    // --- Simulation Logic ---
    useEffect(() => {
        runSimulation();
    }, [simModel, simTokens, simNodes]);

    const runSimulation = () => {
        const modelP = parseFloat(simModel);
        const tokens = parseInt(simTokens);
        const nodes = parseInt(simNodes);

        // Rough Estimations Logic
        const vramRequired = (modelP * 4) / 1; // Basic 4-bit/FP16 logic
        const timeHours = (modelP * tokens * 0.12) / (nodes * 4);
        const efficiency = 95 - (nodes * 2);

        setSimResults({
            time: timeHours.toFixed(1),
            vram: vramRequired.toFixed(0),
            efficiency: efficiency,
            tier: modelP > 40 ? "TIER-1 (Cluster)" : "TIER-2 (Node)"
        });

        setSimChartData({
            labels: ['1 Node', '2 Nodes', '4 Nodes', '8 Nodes'],
            datasets: [{
                label: 'Time (Hrs) Scaling',
                data: [timeHours, timeHours/2, timeHours/4, timeHours/8],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.1)',
                fill: true,
                tension: 0.4
            }]
        });
    };

    return (
        <div className="bg-[#020617] text-slate-100 min-h-screen font-sans overflow-x-hidden">
            {/* Sticky Top Nav */}
            <nav className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-lg border-b border-slate-800">
                <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center space-x-3">
                        <div className="w-4 h-4 bg-sky-500 rounded-full animate-pulse shadow-[0_0_10px_#0ea5e9]"></div>
                        <h1 className="text-xl font-black uppercase tracking-tighter">ISU <span className="text-sky-400">HPC Elite</span></h1>
                    </div>
                    <div className="flex overflow-x-auto space-x-6 text-xs font-bold uppercase tracking-widest no-scrollbar">
                        {['infra', 'models', 'sim', 'roadmap'].map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`pb-1 transition-all ${activeTab === tab ? 'border-b-4 border-sky-400 text-sky-400' : 'text-slate-400 hover:text-slate-200'}`}
                            >
                                {tab === 'infra' ? 'Infrastructure' : tab === 'models' ? 'Top 20 Models' : tab === 'sim' ? 'FT Simulator' : 'Roadmap 2030'}
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto p-6 min-h-screen">
                {/* TAB: INFRASTRUCTURE */}
                {activeTab === 'infra' && (
                    <section className="animate-in fade-in duration-500">
                        <div className="mb-12">
                            <h2 className="text-4xl font-extrabold mb-4">Core Compute Infrastructure</h2>
                            <p className="text-slate-400 max-w-3xl">Detailed technical breakdown of the Dell PowerEdge cluster and NVIDIA acceleration fabric powering ISU's 2025-2030 research goals.</p>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
                            {/* Node Types Chart */}
                            <div className="lg:col-span-2 bg-slate-900/50 border border-sky-400/10 rounded-2xl p-6 h-[400px]">
                                <Bar data={infraData} options={infraOptions} />
                            </div>
                            {/* Quick Stats */}
                            <div className="grid grid-cols-1 gap-4">
                                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                                    <p className="text-xs text-slate-500 uppercase font-bold mb-1">Compute Throughput</p>
                                    <p className="text-3xl font-black text-sky-400">4.2 PetaFlops</p>
                                </div>
                                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                                    <p className="text-xs text-slate-500 uppercase font-bold mb-1">Interconnect Bandwidth</p>
                                    <p className="text-3xl font-black text-purple-400">200 Gbps</p>
                                </div>
                                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
                                    <p className="text-xs text-slate-500 uppercase font-bold mb-1">Global Storage IOPS</p>
                                    <p className="text-3xl font-black text-pink-400">1.2M+</p>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {[
                                { title: "CPU Nodes", desc: "Dell R750 | Intel Xeon Gold 6348 (56T) | 512GB RAM | 2x 1.6TB NVMe", color: "border-sky-500" },
                                { title: "GPU Nodes", desc: "Dell XE8545 | 4x NVIDIA A100 (80GB) | SXM4 Interconnect | 1TB RAM", color: "border-purple-500" },
                                { title: "Data Fabric", desc: "PowerScale F600 | Lustre Parallel FS | HDR InfiniBand | 400TB All-Flash", color: "border-pink-500" },
                                { title: "Login & Mgmt", desc: "Dell R650 | OpenOnDemand Portal | Slurm 23.x | Singularity/Apptainer", color: "border-emerald-500" }
                            ].map((item, idx) => (
                                <div key={idx} className={`bg-slate-800/50 p-6 rounded-xl border-l-4 ${item.color}`}>
                                    <h4 className="font-bold text-white mb-2">{item.title}</h4>
                                    <p className="text-xs text-slate-400">{item.desc}</p>
                                </div>
                            ))}
                        </div>
                    </section>
                )}

                {/* TAB: TOP 20 MODELS */}
                {activeTab === 'models' && (
                    <section className="animate-in fade-in duration-500">
                        <div className="mb-12">
                            <h2 className="text-4xl font-extrabold mb-4">Top 20 Open-Source LLMs</h2>
                            <p className="text-slate-400 max-w-3xl">A curated selection of models optimized for ISU HPC fine-tuning workflows, categorized by parameter density and architecture.</p>
                        </div>

                        <div className="overflow-x-auto bg-slate-900/50 rounded-2xl border border-slate-800">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-slate-800 text-slate-400 uppercase text-[10px] tracking-widest">
                                    <tr>
                                        <th className="p-4">Model Name</th>
                                        <th className="p-4">Params</th>
                                        <th className="p-4">Ctx Window</th>
                                        <th className="p-4">VRAM Reqd</th>
                                        <th className="p-4">Pros & Technical Focus</th>
                                        <th className="p-4">Cons</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {topModels.map((m, idx) => (
                                        <tr key={idx} className="hover:bg-slate-800/50 transition-colors">
                                            <td className="p-4 font-bold text-sky-400">{m.name}</td>
                                            <td className="p-4 font-mono text-xs text-slate-300">{m.params}</td>
                                            <td className="p-4 font-mono text-xs text-slate-300">{m.ctx}</td>
                                            <td className="p-4"><span className="px-2 py-1 bg-slate-800 rounded text-[10px] text-slate-300">{m.vram}</span></td>
                                            <td className="p-4 text-xs text-slate-300"><strong className="text-emerald-400">Pros:</strong> {m.pros}</td>
                                            <td className="p-4 text-xs text-slate-500">{m.cons}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>
                )}

                {/* TAB: FT SIMULATOR */}
                {activeTab === 'sim' && (
                    <section className="animate-in fade-in duration-500">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                            <div>
                                <h2 className="text-4xl font-extrabold mb-4">Fine-Tuning Simulator</h2>
                                <p className="text-slate-400 mb-8">Calculate required resources and estimated training time based on our current HPC specifications.</p>
                                
                                <div className="space-y-6 bg-slate-900 p-8 rounded-2xl border border-slate-800">
                                    <div>
                                        <label className="block text-xs font-bold uppercase text-slate-500 mb-2">Base Model Selection</label>
                                        <select 
                                            value={simModel}
                                            onChange={(e) => setSimModel(e.target.value)}
                                            className="w-full bg-slate-800 border border-slate-700 p-3 rounded-lg outline-none focus:border-sky-500 text-white"
                                        >
                                            <option value="8">Llama-3-8B (8B Parameters)</option>
                                            <option value="70">Llama-3-70B (70B Parameters)</option>
                                            <option value="7">Mistral-v0.3 (7.3B Parameters)</option>
                                            <option value="46">Mixtral-8x7B (46.7B Parameters)</option>
                                            <option value="3">Phi-3-Mini (3.8B Parameters)</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold uppercase text-slate-500 mb-2">Dataset Size (Million Tokens)</label>
                                        <input 
                                            type="range" 
                                            min="10" max="1000" step="10" 
                                            value={simTokens}
                                            onChange={(e) => setSimTokens(e.target.value)}
                                            className="w-full accent-sky-500"
                                        />
                                        <div className="flex justify-between text-[10px] mt-1 text-slate-400">
                                            <span>10M</span>
                                            <span className="text-sky-400 font-bold">{simTokens}M</span>
                                            <span>1B</span>
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-bold uppercase text-slate-500 mb-2">Compute Nodes (NVIDIA A100 x4)</label>
                                        <input 
                                            type="number" 
                                            value={simNodes}
                                            onChange={(e) => setSimNodes(e.target.value)}
                                            min="1" max="8" 
                                            className="w-full bg-slate-800 border border-slate-700 p-3 rounded-lg outline-none focus:border-sky-500 text-white"
                                        />
                                    </div>
                                    <button onClick={runSimulation} className="w-full py-4 bg-sky-600 hover:bg-sky-500 font-bold rounded-xl transition-all shadow-lg text-white">
                                        RECALCULATE ESTIMATES
                                    </button>
                                </div>
                            </div>

                            <div className="flex flex-col gap-6">
                                <div className="bg-slate-900 p-8 rounded-2xl border border-slate-800 flex-1">
                                    <h4 className="text-xl font-bold mb-6 text-sky-400">Simulation Output</h4>
                                    <div className="grid grid-cols-2 gap-6">
                                        {[
                                            { label: "Est. Training Time", val: `${simResults.time} Hrs` },
                                            { label: "Peak VRAM Usage", val: `${simResults.vram} GB` },
                                            { label: "Compute Efficiency", val: `${simResults.efficiency}%` },
                                            { label: "Resource Tier", val: simResults.tier }
                                        ].map((item, idx) => (
                                            <div key={idx} className="p-4 bg-slate-800 rounded-lg">
                                                <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">{item.label}</p>
                                                <p className="text-2xl font-black text-white">{item.val}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                                <div className="bg-slate-900/50 border border-sky-400/10 rounded-2xl p-4 h-[250px]">
                                    <Line 
                                        data={simChartData} 
                                        options={{
                                            responsive: true,
                                            maintainAspectRatio: false,
                                            scales: { 
                                                y: { beginAtZero: true, grid: { color: '#1e293b' } },
                                                x: { ticks: { color: '#64748b' } }
                                            },
                                            plugins: { legend: { display: true, labels: { color: '#cbd5e1' } } }
                                        }} 
                                    />
                                </div>
                            </div>
                        </div>
                    </section>
                )}

                {/* TAB: ROADMAP 2030 */}
                {activeTab === 'roadmap' && (
                    <section className="animate-in fade-in duration-500">
                        <div className="mb-12">
                            <h2 className="text-4xl font-extrabold mb-4">Strategic Evolution Roadmap</h2>
                            <p className="text-slate-400">Phased deployment of SecOps, DevOps, and Adversarial AI modules.</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                            {[
                                { phase: "Phase 1: 2025", border: "border-sky-500", dot: "text-sky-500", items: ["DevOps Automation: Immutable CI/CD pipelines", "SecOps Init: Real-time traffic analysis", "HW Upgrade: HDR 200G InfiniBand"] },
                                { phase: "Phase 2: 2027", border: "border-purple-500", dot: "text-purple-500", items: ["AI Adversarial: Automated red-teaming", "Supply Chain: SBOM integrity verif", "10.0 PetaFlops Expansion"] },
                                { phase: "Phase 3: 2030", border: "border-pink-500", dot: "text-pink-500", items: ["Autonomous SOC: AI-driven response", "Quantum Ready: Testing PQC algos", "Full Multi-Tenant Integrity"] }
                            ].map((p, idx) => (
                                <div key={idx} className={`p-8 bg-slate-900 rounded-3xl border-t-8 ${p.border}`}>
                                    <h3 className="text-2xl font-black mb-4 text-white">{p.phase}</h3>
                                    <ul className="space-y-4 text-sm text-slate-400">
                                        {p.items.map((it, i) => (
                                            <li key={i} className="flex items-start"><span className={`${p.dot} mr-2`}>◈</span> {it}</li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                        
                        <div className="w-full h-96 bg-slate-900 rounded-2xl border border-slate-800 p-4">
                             <Plot
                                data={[
                                  {
                                    x: [2024, 2025, 2026, 2027, 2028, 2029, 2030],
                                    y: [1.2, 2.5, 4.2, 6.8, 8.5, 12.0, 15.0],
                                    type: 'scatter',
                                    mode: 'lines+markers',
                                    marker: {color: '#a855f7', size: 10},
                                    line: {color: '#0ea5e9', width: 4, shape: 'spline'},
                                    name: 'PetaFlops'
                                  },
                                ]}
                                layout={{
                                    autosize: true, 
                                    title: { text: 'Projected Compute Capacity Growth (PetaFlops)', font: { color: '#94a3b8' } },
                                    paper_bgcolor: 'rgba(0,0,0,0)',
                                    plot_bgcolor: 'rgba(0,0,0,0)',
                                    xaxis: { gridcolor: '#1e293b', tickfont: { color: '#64748b' } },
                                    yaxis: { gridcolor: '#1e293b', tickfont: { color: '#64748b' } },
                                    margin: { t: 50, b: 50, l: 50, r: 50 }
                                }}
                                style={{ width: "100%", height: "100%" }}
                                useResizeHandler={true}
                                config={{ displayModeBar: false }}
                              />
                        </div>
                    </section>
                )}
            </main>

            <footer className="py-12 border-t border-slate-800 text-center">
                <p className="text-slate-600 text-[10px] uppercase tracking-widest">© 2025-2030 Istinye University HPC Strategic Division | Verified Architecture</p>
            </footer>
        </div>
    );
};

export default Infographic;
