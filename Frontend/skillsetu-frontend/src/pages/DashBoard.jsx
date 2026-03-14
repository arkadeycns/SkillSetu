import Layout from "../layout/Layout";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

export default function Dashboard() {
  const workers = [
    { name: "Rahul", skill: "Electrician", result: "PASS" },
    { name: "Aman", skill: "Plumber", result: "FAIL" },
    { name: "Suresh", skill: "Carpenter", result: "PASS" },
    { name: "Ravi", skill: "Mechanic", result: "PASS" },
    { name: "Ramesh", skill: "Electrician", result: "PASS" },
    { name: "Karan", skill: "Plumber", result: "FAIL" },
    { name: "Sunil", skill: "Carpenter", result: "PASS" },
    { name: "Deepak", skill: "Mechanic", result: "PASS" },
  ];

  const totalWorkers = workers.length;
  const passCount = workers.filter((w) => w.result === "PASS").length;
  const passRate = Math.round((passCount / totalWorkers) * 100);

  const skillData = [
    { name: "Electrician", value: 4 },
    { name: "Plumber", value: 3 },
    { name: "Carpenter", value: 2 },
    { name: "Mechanic", value: 1 },
  ];

  const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444"];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}

        <div className="bg-white p-5 rounded-xl shadow text-center">
          <h1 className="text-2xl font-bold text-black">
            Government Dashboard
          </h1>

          <p className="text-gray-600 text-sm">
            Monitor worker skill verification records
          </p>
        </div>

        {/* Stats Cards */}

        <div className="grid grid-cols-3 gap-5">
          <div className="bg-slate-900 text-white p-4 rounded-xl shadow text-center">
            <p className="text-gray-400 text-sm">Total Workers</p>
            <h2 className="text-2xl font-bold">{totalWorkers}</h2>
          </div>

          <div className="bg-slate-900 text-white p-4 rounded-xl shadow text-center">
            <p className="text-gray-400 text-sm">Workers Passed</p>
            <h2 className="text-2xl font-bold text-green-400">{passCount}</h2>
          </div>

          <div className="bg-slate-900 text-white p-4 rounded-xl shadow text-center">
            <p className="text-gray-400 text-sm">Pass Rate</p>
            <h2 className="text-2xl font-bold text-blue-400">{passRate}%</h2>
          </div>
        </div>

        {/* Chart + Table */}

        <div className="grid grid-cols-2 gap-5">
          {/* Pie Chart */}

          <div className="bg-slate-900 p-5 rounded-xl shadow h-[320px]">
            <h2 className="text-white text-lg font-semibold mb-3 text-center">
              Skill Distribution
            </h2>

            <div className="h-[240px]">
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={skillData}
                    cx="50%"
                    cy="50%"
                    outerRadius={85}
                    dataKey="value"
                    label
                  >
                    {skillData.map((entry, index) => (
                      <Cell key={index} fill={COLORS[index]} />
                    ))}
                  </Pie>

                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Worker Table */}

          <div className="bg-slate-900 p-5 rounded-xl shadow h-[320px] flex flex-col">
            <h2 className="text-white text-lg font-semibold mb-3">
              Worker Verification
            </h2>

            {/* Scrollable Table */}

            <div className="overflow-y-auto flex-1">
              <table className="w-full text-white text-sm">
                <thead className="border-b border-gray-600 sticky top-0 bg-slate-900">
                  <tr>
                    <th className="text-left py-2">Worker</th>
                    <th className="text-left">Skill</th>
                    <th className="text-left">Result</th>
                  </tr>
                </thead>

                <tbody>
                  {workers.map((worker, index) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="py-2">{worker.name}</td>

                      <td>{worker.skill}</td>

                      <td
                        className={
                          worker.result === "PASS"
                            ? "text-green-400"
                            : "text-red-400"
                        }
                      >
                        {worker.result}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
