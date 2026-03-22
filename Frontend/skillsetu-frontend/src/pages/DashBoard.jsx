import React, { useState, useEffect } from "react";
import Layout from "../layout/Layout";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  Activity,
  TrendingUp,
  Award,
  Briefcase,
} from "lucide-react";

export default function Dashboard() {
  // --- STATE ---
  const [stats, setStats] = useState({
    totalWorkers: 0,
    passCount: 0,
    passRate: 0,
    liveFeed: [],
    skillData: [],
  });

  const [loading, setLoading] = useState(true);

  const GOLD_COLORS = ["#eab308", "#facc15", "#fef08a", "#a16207", "#ca8a04", "#854d0e"];

  // --- FETCH REAL DATA ---
  const loadData = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/admin/stats");
      const data = await response.json();

      setStats({
        totalWorkers: data.totalWorkers || 0,
        passCount: data.passCount || 0,
        passRate: data.passRate || 0,
        liveFeed: data.liveFeed || [],
        skillData: data.skillData || [], 
      });

      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const { totalWorkers, passCount, passRate, liveFeed, skillData } = stats;

  // --- LOADING SCREEN ---
  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center text-white bg-slate-900">
          <p className="text-lg animate-pulse font-bold text-yellow-500">Loading Command Center...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-slate-900 text-slate-200 py-8 px-4 sm:px-6 lg:px-8 font-sans">
        <div className="max-w-7xl mx-auto space-y-8">

          {/* Header */}
          <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <TrendingUp size={120} className="text-yellow-500" />
            </div>
            <div className="relative z-10">
              <div className="inline-block px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-xs text-yellow-500 uppercase font-bold mb-4">
                Official Admin Portal
              </div>
              <h1 className="text-4xl font-extrabold text-white">
                Skill<span className="text-yellow-500">Setu</span> Command Center
              </h1>
              <p className="text-slate-400 mt-2 text-lg">
                National competency oversight. Monitoring live AI-verified trade assessments.
              </p>
            </div>
          </div>

          {/* KPI CARDS */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Total */}
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 hover:border-yellow-500/30 transition-all">
              <div className="flex justify-between mb-4">
                <Briefcase className="text-yellow-500" size={28} />
                <span className="text-xs font-bold text-slate-500 uppercase">Live DB</span>
              </div>
              <p className="text-slate-400 text-sm uppercase tracking-wider font-semibold">Total Assessments</p>
              <h2 className="text-4xl font-bold text-white mt-1">{totalWorkers}</h2>
            </div>

            {/* Pass */}
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 hover:border-yellow-500/30 transition-all">
              <div className="flex justify-between mb-4">
                <Award className="text-yellow-500" size={28} />
                <span className="text-xs font-bold text-green-500 uppercase">Verified</span>
              </div>
              <p className="text-slate-400 text-sm uppercase tracking-wider font-semibold">Certified Personnel</p>
              <h2 className="text-4xl font-bold text-yellow-500 mt-1">{passCount}</h2>
            </div>

            {/* Rate */}
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 hover:border-yellow-500/30 transition-all">
              <div className="flex justify-between mb-4">
                <Activity className="text-yellow-500" size={28} />
                <span className="text-xs font-bold text-yellow-500 uppercase">Real-Time</span>
              </div>
              <p className="text-slate-400 text-sm uppercase tracking-wider font-semibold">National Pass Rate</p>
              <h2 className="text-4xl font-bold text-white mt-1">{passRate}%</h2>
            </div>
          </div>

          {/* MAIN SECTION */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* PIE CHART */}
            <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700 h-[450px] shadow-xl flex flex-col">
              <div className="flex items-center gap-3 mb-6">
                 <div className="w-1 h-6 bg-yellow-500 rounded-full"></div>
                 <h2 className="text-white text-xl font-bold tracking-tight">Trade Distribution</h2>
              </div>

              {skillData.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-3">
                  <PieChart className="opacity-20" size={48} />
                  <p>Awaiting first assessment data...</p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={skillData}
                      cx="50%"
                      cy="45%"
                      innerRadius={70}
                      outerRadius={110}
                      paddingAngle={5}
                      dataKey="value"
                      nameKey="name" 
                      stroke="none"
                    >
                      {skillData.map((_, i) => (
                        <Cell key={i} fill={GOLD_COLORS[i % GOLD_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value, name) => [value, name]} 
                      contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', color: '#fff' }}
                      itemStyle={{ color: '#eab308', fontWeight: 'bold' }}
                    />
                    <Legend verticalAlign="bottom" height={36} formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* TABLE */}
            <div className="bg-slate-800/50 rounded-3xl border border-slate-700 h-[450px] flex flex-col overflow-hidden shadow-xl">
              <div className="p-6 border-b border-slate-700 flex items-center justify-between bg-slate-800/30">
                <div className="flex items-center gap-3">
                    <div className="w-1 h-6 bg-yellow-500 rounded-full"></div>
                    <h2 className="text-white text-xl font-bold tracking-tight">Live Certification Feed</h2>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full animate-ping"></span>
                    <span className="text-[10px] text-yellow-500 font-bold uppercase tracking-widest">Live Updates</span>
                </div>
              </div>

              <div className="overflow-y-auto flex-1 custom-scrollbar">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-500 uppercase bg-slate-900/50 sticky top-0 z-10">
                    <tr>
                      <th className="px-6 py-4 font-bold tracking-wider">Candidate</th>
                      <th className="px-6 py-4 font-bold tracking-wider">Applied Trade</th>
                      <th className="px-6 py-4 font-bold tracking-wider">Timestamp</th>
                      <th className="px-6 py-4 font-bold tracking-wider text-right">Verification</th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-700/50">
                    {liveFeed.length === 0 ? (
                      <tr>
                        <td colSpan="4" className="text-center py-10 text-slate-500 italic">
                          No recent activity.
                        </td>
                      </tr>
                    ) : (
                      liveFeed.map((worker, index) => (
                        <tr key={index} className="hover:bg-yellow-500/5 transition-colors">
                          <td className="px-6 py-4 font-bold text-slate-200">{worker.name}</td>
                          <td className="px-6 py-4 text-slate-400">{worker.skill}</td>
                          <td className="px-6 py-4 text-slate-500 font-mono text-xs">{worker.date}</td>
                          <td className="px-6 py-4 text-right">
                            <span className={`px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-widest border ${
                              worker.result === "PASS" 
                                ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20" 
                                : "bg-red-500/10 text-red-500 border-red-500/20"
                            }`}>
                              {worker.result}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>
      </div>
    </Layout>
  );
}