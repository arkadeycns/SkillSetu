import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleLinear } from "d3-scale";
import Layout from "../layout/Layout";
import { TrendingUp, RefreshCw } from "lucide-react";

const INDIA_MAP =
  "https://raw.githubusercontent.com/india-in-data/india-states-2019/master/india_states.geojson";

const initialData = [
  { id: "Uttar Pradesh", count: 850 },
  { id: "Maharashtra", count: 720 },
  { id: "Bihar", count: 600 },
  { id: "West Bengal", count: 500 },
  { id: "Tamil Nadu", count: 450 },
  { id: "Karnataka", count: 400 },
  { id: "Gujarat", count: 380 },
];

const colorScale = scaleLinear()
  .domain([0, 1000])
  .range(["#1e293b", "#eab308"]);

export default function RegionalReports() {
  const navigate = useNavigate();
  const [data, setData] = useState(initialData);
  const [hoveredState, setHoveredState] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const simulateNewAssessment = () => {
    setIsSyncing(true);

    setTimeout(() => {
      setData((prev) =>
        prev.map((item) =>
          item.id === "Uttar Pradesh"
            ? { ...item, count: item.count + 15 }
            : item
        )
      );
      setIsSyncing(false);
    }, 1000);
  };

  return (
    <Layout>
      <div className="min-h-screen bg-slate-900 text-slate-200 p-6 md:p-12">
        <div className="max-w-7xl mx-auto mb-10">
          <button
            onClick={() => navigate("/")}
            className="text-slate-400 hover:text-yellow-500 transition-colors flex items-center gap-2 text-sm font-semibold mb-4"
          >
            ← Back to Command Center
          </button>

          <h1 className="text-4xl font-bold text-white tracking-tight">
            National <span className="text-yellow-500">Skill Heatmap</span>
          </h1>
        </div>

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* MAP */}
          <div className="lg:col-span-2 bg-slate-800/40 border border-slate-700 rounded-3xl p-4 relative">

            {/* Hover Card */}
            <div className="absolute top-4 left-4 z-10 bg-slate-900/90 p-4 rounded-xl border border-slate-700 backdrop-blur-md">
              <p className="text-xs font-bold text-slate-500 uppercase">
                State Info
              </p>
              <p className="text-lg font-bold text-white">
                {hoveredState ? hoveredState.id : "Hover over Map"}
              </p>
              <p className="text-yellow-500 font-mono">
                {hoveredState ? `${hoveredState.count} Workers` : "--"}
              </p>
            </div>

            {/* Map Container */}
            <div style={{ width: "100%", height: "600px" }}>
              <ComposableMap
                projection="geoMercator"
                projectionConfig={{
                  scale: 900,
                  center: [82, 22],
                }}
                style={{ width: "100%", height: "100%" }}
              >
                <Geographies geography={INDIA_MAP}>
                  {({ geographies }) =>
                    geographies.map((geo) => {
                      const stateName = geo.properties.name;

                      const stateData = data.find(
                        (s) => s.id === stateName
                      );

                      return (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          onMouseEnter={() =>
                            setHoveredState(
                              stateData || { id: stateName, count: 0 }
                            )
                          }
                          onMouseLeave={() => setHoveredState(null)}
                          style={{
                            default: {
                              fill: stateData
                                ? colorScale(stateData.count)
                                : "#0f172a",
                              stroke: "#334155",
                              strokeWidth: 0.5,
                              outline: "none",
                            },
                            hover: {
                              fill: "#facc15",
                              stroke: "#000",
                              outline: "none",
                              cursor: "pointer",
                            },
                            pressed: {
                              fill: "#eab308",
                              outline: "none",
                            },
                          }}
                        />
                      );
                    })
                  }
                </Geographies>
              </ComposableMap>
            </div>
          </div>

          {/* SIDEBAR */}
          <div className="space-y-6">
            <button
              onClick={simulateNewAssessment}
              className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-yellow-500 text-slate-900 rounded-xl font-bold transition-all hover:bg-yellow-400"
            >
              <RefreshCw
                size={20}
                className={isSyncing ? "animate-spin" : ""}
              />
              Simulate Test Completion
            </button>

            <div className="bg-slate-800/40 border border-slate-700 rounded-3xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp size={20} className="text-yellow-500" />
                Top Regions
              </h3>

              {data.slice(0, 5).map((item, idx) => (
                <div
                  key={idx}
                  className="flex justify-between py-2 border-b border-slate-700 last:border-0"
                >
                  <span className="text-slate-400">{item.id}</span>
                  <span className="text-yellow-500 font-bold">
                    {item.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}