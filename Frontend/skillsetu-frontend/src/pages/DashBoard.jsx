import Layout from "../layout/Layout";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Users, UserCheck, Activity } from "lucide-react";

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

  const districtHeatmap = [
    { name: "Prayagraj", passRate: 45, metric: "Failing Electrical Safety", status: "critical" },
    { name: "Varanasi", passRate: 78, metric: "Stable Supply", status: "good" },
    { name: "Kanpur", passRate: 52, metric: "Low Carpentry Skills", status: "warning" },
    { name: "Lucknow", passRate: 88, metric: "High Competency", status: "excellent" },
    { name: "Agra", passRate: 35, metric: "Critical Plumbing Shortage", status: "critical" },
    { name: "Noida", passRate: 92, metric: "Oversupplied", status: "excellent" },
  ];

  // --- CALCULATIONS & HELPERS ---
  
  const totalWorkers = workers.length;
  const passCount = workers.filter((w) => w.result === "PASS").length;
  const passRate = Math.round((passCount / totalWorkers) * 100);

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

  const getHeatColor = (status) => {
    switch(status) {
      case "critical": return "bg-red-500 text-white shadow-red-200";
      case "warning": return "bg-amber-400 text-amber-950 shadow-amber-200";
      case "good": return "bg-emerald-400 text-white shadow-emerald-200";
      case "excellent": return "bg-emerald-600 text-white shadow-emerald-200";
      default: return "bg-gray-200 text-gray-800";
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-8">
          
          {/* Header */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
              Regional Skill Command Center
            </h1>
            <p className="text-slate-500 mt-2 text-lg">
              Live monitoring of district-level vocational competency verification.
            </p>
          </div>

          {/* KPI Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-slate-500 text-sm font-semibold uppercase tracking-wider mb-1">Total Assessments</p>
                <h2 className="text-4xl font-bold text-slate-900">{totalWorkers}</h2>
              </div>
              <div className="bg-blue-100 p-4 rounded-full">
                <Users size={32} className="text-blue-600" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-slate-500 text-sm font-semibold uppercase tracking-wider mb-1">Verified Workers</p>
                <h2 className="text-4xl font-bold text-emerald-600">{passCount}</h2>
              </div>
              <div className="bg-emerald-100 p-4 rounded-full">
                <UserCheck size={32} className="text-emerald-600" />
              </div>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex items-center justify-between">
              <div>
                <p className="text-slate-500 text-sm font-semibold uppercase tracking-wider mb-1">Pass Rate</p>
                <h2 className="text-4xl font-bold text-amber-500">{passRate}%</h2>
              </div>
              <div className="bg-amber-100 p-4 rounded-full">
                <Activity size={32} className="text-amber-600" />
              </div>
            </div>
          </div>

          {/* District-Level Heatmap Section */}
          <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex justify-between items-end mb-6">
              <div>
                <h2 className="text-slate-800 text-xl font-bold">District-Level Skill Gap Heatmap</h2>
                <p className="text-slate-500 text-sm mt-1">Live intervention alerts based on assessment pass rates.</p>
              </div>
              <div className="flex gap-3 text-xs font-semibold text-slate-500 uppercase">
                <span className="flex items-center gap-1"><div className="w-3 h-3 bg-red-500 rounded-full"></div> Critical</span>
                <span className="flex items-center gap-1"><div className="w-3 h-3 bg-amber-400 rounded-full"></div> Warning</span>
                <span className="flex items-center gap-1"><div className="w-3 h-3 bg-emerald-500 rounded-full"></div> Healthy</span>
              </div>
            </div>

            {/* The CSS Grid Heatmap */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {districtHeatmap.map((district, idx) => (
                <div 
                  key={idx} 
                  className={`${getHeatColor(district.status)} p-5 rounded-xl shadow-sm transition-transform hover:-translate-y-1 cursor-pointer flex flex-col justify-between min-h-[120px]`}
                >
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-lg opacity-90">{district.name}</h3>
                    <span className="text-2xl font-black opacity-80">{district.passRate}%</span>
                  </div>
                  <div className="mt-4 text-sm font-medium opacity-90 leading-tight">
                    {district.status === "critical" && "⚠️ "} 
                    {district.metric}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Main Content Area: Chart + Table */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Pie Chart */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 h-[400px] flex flex-col">
              <h2 className="text-slate-800 text-xl font-bold mb-6">
                Demand by Trade (District X)
              </h2>
              <div className="flex-1 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={skillData}
                      cx="50%"
                      cy="45%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {skillData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend verticalAlign="bottom" height={36} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Live Worker Feed Table */}
            <div className="bg-white p-0 rounded-2xl shadow-sm border border-slate-200 h-[400px] flex flex-col overflow-hidden">
              <div className="p-6 border-b border-slate-100">
                <h2 className="text-slate-800 text-xl font-bold">
                  Live Verification Feed
                </h2>
              </div>
              
              <div className="overflow-y-auto flex-1 p-2">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-500 uppercase bg-slate-50 sticky top-0 z-10">
                    <tr>
                      <th className="px-6 py-4 font-semibold rounded-tl-lg">Worker Name</th>
                      <th className="px-6 py-4 font-semibold">Trade</th>
                      <th className="px-6 py-4 font-semibold">Date</th>
                      <th className="px-6 py-4 font-semibold rounded-tr-lg text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workers.map((worker, index) => (
                      <tr key={index} className="bg-white border-b border-slate-50 hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-900">{worker.name}</td>
                        <td className="px-6 py-4 text-slate-600">{worker.skill}</td>
                        <td className="px-6 py-4 text-slate-500">{worker.date}</td>
                        <td className="px-6 py-4 text-right">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                            worker.result === "PASS" 
                              ? "bg-emerald-100 text-emerald-700" 
                              : "bg-red-100 text-red-700"
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