import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { ComposableMap, Geographies, Geography } from "react-simple-maps";
import { scaleLinear } from "d3-scale";
import Layout from "../layout/Layout";
import { TrendingUp, RefreshCw } from "lucide-react";

const INDIA_MAP = "https://raw.githubusercontent.com/india-in-data/india-states-2019/master/india_states.geojson";

export default function RegionalReports() {
  const navigate = useNavigate();
  const [data, setData] = useState([]); 
  const [hoveredState, setHoveredState] = useState(null);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchMapData = async () => {
    setIsSyncing(true);
    try {
      const response = await fetch("http://localhost:8000/api/admin/stats");
      const result = await response.json();
      
      if (result.heatmapData) {
        setData(result.heatmapData);
      }
    } catch (error) {
      console.error("Failed to fetch heatmap data:", error);
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchMapData();
    const interval = setInterval(fetchMapData, 5000);
    return () => clearInterval(interval);
  }, []);

  const maxWorkers = data.length > 0 ? Math.max(...data.map(d => d.count)) : 10;
  
  const colorScale = scaleLinear()
    .domain([0, maxWorkers])
    .range(["#1e293b", "#eab308"]); 

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
          <div className="lg:col-span-2 bg-slate-800/40 border border-slate-700 rounded-3xl p-4 relative shadow-xl">
            {/* Hover Card */}
            <div className="absolute top-4 left-4 z-10 bg-slate-900/90 p-4 rounded-xl border border-slate-700 backdrop-blur-md pointer-events-none">
              <p className="text-xs font-bold text-slate-500 uppercase">State Info</p>
              <p className="text-lg font-bold text-white">
                {hoveredState ? hoveredState.id : "Hover over Map"}
              </p>
              <p className="text-yellow-500 font-mono">
                {hoveredState ? `${hoveredState.count} Verified Workers` : "--"}
              </p>
            </div>

            <div style={{ width: "100%", height: "600px" }}>
              <ComposableMap
                projection="geoMercator"
                projectionConfig={{ scale: 900, center: [82, 22] }}
                style={{ width: "100%", height: "100%" }}
              >
                <Geographies geography={INDIA_MAP}>
                  {({ geographies }) =>
                    geographies.map((geo) => {
                      
                      const stateName = 
                        geo.properties.st_nm || 
                        geo.properties.ST_NM || 
                        geo.properties.name || 
                        geo.properties.NAME_1 || 
                        "Unknown State";

                      const stateData = data.find(
                        (s) => s.id && stateName && s.id.toLowerCase().trim() === stateName.toLowerCase().trim()
                      );

                      return (
                        <Geography
                          key={geo.rsmKey}
                          geography={geo}
                          onMouseEnter={() => setHoveredState(stateData || { id: stateName, count: 0 })}
                          onMouseLeave={() => setHoveredState(null)}
                          style={{
                            default: {
                              fill: stateData ? colorScale(stateData.count) : "#0f172a",
                              stroke: "#334155",
                              strokeWidth: 0.5,
                              outline: "none",
                              transition: "all 250ms",
                            },
                            hover: { fill: "#facc15", stroke: "#000", outline: "none", cursor: "pointer" },
                            pressed: { fill: "#eab308", outline: "none" },
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
              onClick={fetchMapData}
              className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-yellow-500 text-slate-900 rounded-xl font-bold transition-all hover:bg-yellow-400 shadow-lg shadow-yellow-500/20"
            >
              <RefreshCw size={20} className={isSyncing ? "animate-spin" : ""} />
              {isSyncing ? "Syncing..." : "Refresh Live Data"}
            </button>

            <div className="bg-slate-800/40 border border-slate-700 rounded-3xl p-6 shadow-xl">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp size={20} className="text-yellow-500" />
                Top Regions
              </h3>
              
              {data.length === 0 ? (
                 <p className="text-slate-500 text-sm italic">No verification data yet. Waiting for assessments...</p>
              ) : (
                [...data]
                  .sort((a, b) => b.count - a.count)
                  .slice(0, 5)
                  .map((item, idx) => (
                  <div key={idx} className="flex justify-between items-center py-3 border-b border-slate-700 last:border-0">
                    <span className="text-slate-300 font-medium">{item.id}</span>
                    <span className="text-slate-900 bg-yellow-500 px-3 py-1 rounded-full text-xs font-black">
                      {item.count}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}