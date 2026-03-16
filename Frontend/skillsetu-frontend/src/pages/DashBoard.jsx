import React from "react";
import Layout from "../layout/Layout";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Users, UserCheck, Activity, TrendingUp, Award, Briefcase } from "lucide-react";

export default function Dashboard() {
  // --- MOCK DATA ---
  const workers = [
    { name: "Rahul Sharma", skill: "Electrician", result: "PASS", date: "Oct 24" },
    { name: "Aman Gupta", skill: "Plumber", result: "FAIL", date: "Oct 24" },
    { name: "Suresh Verma", skill: "Carpenter", result: "PASS", date: "Oct 23" },
    { name: "Ravi Kumar", skill: "Mechanic", result: "PASS", date: "Oct 23" },
    { name: "Ramesh Singh", skill: "Electrician", result: "PASS", date: "Oct 22" },
    { name: "Karan Patel", skill: "Plumber", result: "FAIL", date: "Oct 22" },
    { name: "Sunil Das", skill: "Carpenter", result: "PASS", date: "Oct 21" },
    { name: "Deepak Yadav", skill: "Mechanic", result: "PASS", date: "Oct 21" },
  ];

  const skillData = [
    { name: "Electrician", value: 4 },
    { name: "Plumber", value: 3 },
    { name: "Carpenter", value: 2 },
    { name: "Mechanic", value: 1 },
  ];

  // --- CALCULATIONS ---
  const totalWorkers = workers.length;
  const passCount = workers.filter((w) => w.result === "PASS").length;
  const passRate = Math.round((passCount / totalWorkers) * 100);

  // Premium Gold Palette for Charts
  const GOLD_COLORS = ["#eab308", "#facc15", "#fef08a", "#a16207"];

  return (
    <Layout>
      <div className="min-h-screen bg-slate-900 text-slate-200 py-8 px-4 sm:px-6 lg:px-8 font-sans">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Header Section */}
          <div className="bg-slate-800/50 backdrop-blur-md p-8 rounded-3xl border border-slate-700 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-10">
              <TrendingUp size={120} className="text-yellow-500" />
            </div>
            <div className="relative z-10">
                <div className="inline-block px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-xs text-yellow-500 tracking-widest uppercase font-bold mb-4">
                    Official Admin Portal
                </div>
                <h1 className="text-4xl font-extrabold text-white tracking-tight">
                    Skill<span className="text-yellow-500">Setu</span> Command Center
                </h1>
                <p className="text-slate-400 mt-2 text-lg max-w-2xl">
                    National competency oversight. Monitor live AI-verified trade assessments and workforce certification flows.
                </p>
            </div>
          </div>

          {/* KPI Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* Total Assessments */}
            <div className="bg-slate-800/50 backdrop-blur-md p-6 rounded-2xl border border-slate-700 hover:border-yellow-500/30 transition-all group">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-yellow-500/10 p-3 rounded-xl border border-yellow-500/20 group-hover:scale-110 transition-transform">
                  <Briefcase size={24} className="text-yellow-500" />
                </div>
                <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">Growth: +12%</span>
              </div>
              <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Total Assessments</p>
              <h2 className="text-4xl font-bold text-white mt-1">{totalWorkers}</h2>
            </div>

            {/* Verified Workers */}
            <div className="bg-slate-800/50 backdrop-blur-md p-6 rounded-2xl border border-slate-700 hover:border-yellow-500/30 transition-all group">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-yellow-500/10 p-3 rounded-xl border border-yellow-500/20 group-hover:scale-110 transition-transform">
                  <Award size={24} className="text-yellow-500" />
                </div>
                <span className="text-xs font-bold text-emerald-500 uppercase tracking-tighter">Verified</span>
              </div>
              <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Certified Personnel</p>
              <h2 className="text-4xl font-bold text-yellow-500 mt-1">{passCount}</h2>
            </div>

            {/* Pass Rate */}
            <div className="bg-slate-800/50 backdrop-blur-md p-6 rounded-2xl border border-slate-700 hover:border-yellow-500/30 transition-all group">
              <div className="flex items-center justify-between mb-4">
                <div className="bg-yellow-500/10 p-3 rounded-xl border border-yellow-500/20 group-hover:scale-110 transition-transform">
                  <Activity size={24} className="text-yellow-500" />
                </div>
                <span className="text-xs font-bold text-yellow-500 uppercase tracking-tighter">Real-Time</span>
              </div>
              <p className="text-slate-400 text-sm font-semibold uppercase tracking-wider">Quality Benchmark</p>
              <h2 className="text-4xl font-bold text-white mt-1">{passRate}%</h2>
            </div>
          </div>

          {/* Main Content Area: Chart + Table */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Pie Chart Card */}
            <div className="bg-slate-800/50 backdrop-blur-md p-8 rounded-3xl border border-slate-700 h-[450px] flex flex-col shadow-xl">
              <div className="flex items-center gap-3 mb-6">
                 <div className="w-1 h-6 bg-yellow-500 rounded-full"></div>
                 <h2 className="text-white text-xl font-bold tracking-tight">Trade Distribution Analysis</h2>
              </div>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={skillData}
                      cx="50%"
                      cy="45%"
                      innerRadius={70}
                      outerRadius={110}
                      paddingAngle={8}
                      dataKey="value"
                      stroke="none"
                    >
                      {skillData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={GOLD_COLORS[index % GOLD_COLORS.length]} className="focus:outline-none" />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', color: '#fff' }}
                      itemStyle={{ color: '#eab308' }}
                    />
                    <Legend 
                        verticalAlign="bottom" 
                        height={36} 
                        formatter={(value) => <span className="text-slate-400 text-sm font-medium">{value}</span>}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Live Worker Feed Table Card */}
            <div className="bg-slate-800/50 backdrop-blur-md rounded-3xl border border-slate-700 h-[450px] flex flex-col overflow-hidden shadow-xl">
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
                    {workers.map((worker, index) => (
                      <tr key={index} className="hover:bg-yellow-500/5 transition-colors group">
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
                    ))}
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