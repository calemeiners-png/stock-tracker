import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

const API = "https://stock-tracker-6acy.onrender.com";

const CATEGORY_ICONS = {
  "Indices": "📊",
  "Tech": "💻",
  "Finance": "🏦",
  "Energy": "⚡",
  "Health": "🏥",
  "Consumer": "🛒",
  "Crypto": "🪙",
  "EV & Auto": "🚗",
};

export default function Market({ onBack }) {
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedTicker, setSelectedTicker] = useState("SPY");
  const [chartData, setChartData] = useState([]);
  const [chartPeriod, setChartPeriod] = useState("1mo");
  const [loadingChart, setLoadingChart] = useState(false);
  const [stockInfo, setStockInfo] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"];

  useEffect(() => {
    fetchMarket();
    const interval = setInterval(fetchMarket, 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedTicker) {
      fetchChart(selectedTicker, chartPeriod);
      fetchStockInfo(selectedTicker);
    }
  }, [selectedTicker]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchMarket = async () => {
    try {
      const res = await fetch(`${API}/market`);
      const data = await res.json();
      setMarketData(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (e) {
      console.error("Failed to fetch market data");
    }
    setLoading(false);
  };

  const fetchChart = async (ticker, period) => {
    setLoadingChart(true);
    try {
      const res = await fetch(`${API}/chart/${ticker}?period=${period}`);
      const data = await res.json();
      setChartData(data.data || []);
    } catch (e) {
      setChartData([]);
    }
    setLoadingChart(false);
  };

  const fetchStockInfo = async (ticker) => {
    try {
      const res = await fetch(`${API}/stock/${ticker}`);
      const data = await res.json();
      setStockInfo(data);
    } catch (e) {
      setStockInfo(null);
    }
  };

  const handleSelect = (ticker) => {
    setSelectedTicker(ticker);
    fetchChart(ticker, chartPeriod);
    fetchStockInfo(ticker);
  };

  const handlePeriod = (period) => {
    setChartPeriod(period);
    fetchChart(selectedTicker, period);
  };

  const selectedData = Object.values(marketData).flat().find((s) => s?.ticker === selectedTicker);
  const isUp = selectedData?.direction === "up";
  const chartColor = isUp ? "#22c55e" : "#ef4444";

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <button style={styles.backBtn} onClick={onBack}>← Back</button>
        <h1 style={styles.headerTitle}>📊 Market Overview</h1>
        <div style={styles.headerRight}>
          {lastUpdated && <span style={styles.updated}>Updated {lastUpdated}</span>}
        </div>
      </div>

      <div style={styles.layout}>
        {/* Left Panel — Stock List */}
        <div style={styles.leftPanel}>
          {loading && <div style={styles.loadingText}>Loading market data...</div>}
          {Object.entries(marketData).map(([category, stocks]) => (
            <div key={category} style={styles.category}>
              <div style={styles.categoryTitle}>
                {CATEGORY_ICONS[category]} {category}
              </div>
              {stocks.map((stock) => (
                <div
                  key={stock.ticker}
                  style={{
                    ...styles.stockRow,
                    ...(selectedTicker === stock.ticker ? styles.stockRowActive : {})
                  }}
                  onClick={() => handleSelect(stock.ticker)}
                >
                  <div style={styles.stockRowLeft}>
                    <div style={styles.stockRowTicker}>{stock.ticker}</div>
                  </div>
                  <div style={styles.stockRowRight}>
                    <div style={styles.stockRowPrice}>
                      {stock.price ? `$${stock.price}` : "—"}
                    </div>
                    <div style={{
                      ...styles.stockRowChange,
                      color: stock.direction === "up" ? "#22c55e" : "#ef4444"
                    }}>
                      {stock.direction === "up" ? "▲" : "▼"} {Math.abs(stock.change_pct)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Right Panel — Chart */}
        <div style={styles.rightPanel}>
          {selectedData && (
            <div style={styles.chartHeader}>
              <div>
                <h2 style={styles.chartTicker}>{selectedTicker}</h2>
                {stockInfo && (
                  <div style={styles.chartName}>{stockInfo.name}</div>
                )}
              </div>
              <div style={styles.chartPriceBlock}>
                <div style={styles.chartPrice}>
                  {selectedData.price ? `$${selectedData.price}` : "—"}
                </div>
                <div style={{
                  ...styles.chartChange,
                  color: isUp ? "#22c55e" : "#ef4444"
                }}>
                  {isUp ? "▲" : "▼"} {Math.abs(selectedData.change_pct)}%
                </div>
              </div>
            </div>
          )}

          <div style={styles.periodRow}>
            {periods.map((p) => (
              <button
                key={p}
                style={{
                  ...styles.periodBtn,
                  ...(chartPeriod === p ? styles.periodActive : {})
                }}
                onClick={() => handlePeriod(p)}
              >
                {p}
              </button>
            ))}
          </div>

          {loadingChart && (
            <div style={styles.chartLoading}>Loading chart...</div>
          )}

          {!loadingChart && chartData.length > 0 && (
            <div style={styles.chartWrap}>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    tickLine={false}
                    interval={Math.floor(chartData.length / 6)}
                  />
                  <YAxis
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    tickLine={false}
                    axisLine={false}
                    domain={["auto", "auto"]}
                    tickFormatter={(v) => `$${v}`}
                    width={70}
                  />
                  <Tooltip
                    contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }}
                    labelStyle={{ color: "#94a3b8" }}
                    itemStyle={{ color: chartColor }}
                    formatter={(v) => [`$${v}`, "Price"]}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke={chartColor}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 5, fill: chartColor }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {stockInfo && (
            <div style={styles.statsRow}>
              <div style={styles.stat}>
                <div style={styles.statLabel}>Volume</div>
                <div style={styles.statValue}>{stockInfo.volume ? stockInfo.volume.toLocaleString() : "N/A"}</div>
              </div>
              <div style={styles.stat}>
                <div style={styles.statLabel}>Market Cap</div>
                <div style={styles.statValue}>
                  {stockInfo.market_cap
                    ? stockInfo.market_cap >= 1e12
                      ? `$${(stockInfo.market_cap / 1e12).toFixed(2)}T`
                      : `$${(stockInfo.market_cap / 1e9).toFixed(2)}B`
                    : "N/A"}
                </div>
              </div>
              <div style={styles.stat}>
                <div style={styles.statLabel}>52w Change</div>
                <div style={{ ...styles.statValue, color: stockInfo.change_pct >= 0 ? "#22c55e" : "#ef4444" }}>
                  {stockInfo.change_pct ? `${(stockInfo.change_pct * 100).toFixed(2)}%` : "N/A"}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", background: "#0f172a", display: "flex", flexDirection: "column" },
  header: { display: "flex", alignItems: "center", justifyContent: "space-between", padding: "1rem 1.5rem", borderBottom: "1px solid #1e293b", background: "#0f172a" },
  backBtn: { padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid #334155", background: "transparent", color: "#94a3b8", fontSize: "0.9rem", cursor: "pointer" },
  headerTitle: { color: "#f1f5f9", fontSize: "1.25rem", margin: 0 },
  headerRight: { minWidth: "120px", textAlign: "right" },
  updated: { color: "#64748b", fontSize: "0.8rem" },
  layout: { display: "flex", flex: 1, overflow: "hidden" },
  leftPanel: { width: "220px", minWidth: "220px", borderRight: "1px solid #1e293b", overflowY: "auto", padding: "0.5rem 0" },
  loadingText: { color: "#64748b", padding: "1rem", fontSize: "0.85rem" },
  category: { marginBottom: "0.5rem" },
  categoryTitle: { color: "#64748b", fontSize: "0.75rem", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.05em", padding: "0.5rem 1rem", marginTop: "0.5rem" },
  stockRow: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 1rem", cursor: "pointer", borderRadius: "4px", margin: "0 4px" },
  stockRowActive: { background: "#1e293b" },
  stockRowLeft: {},
  stockRowTicker: { color: "#f1f5f9", fontSize: "0.9rem", fontWeight: "600" },
  stockRowRight: { textAlign: "right" },
  stockRowPrice: { color: "#f1f5f9", fontSize: "0.85rem" },
  stockRowChange: { fontSize: "0.75rem" },
  rightPanel: { flex: 1, padding: "1.5rem", overflowY: "auto" },
  chartHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" },
  chartTicker: { color: "#f1f5f9", fontSize: "2rem", margin: 0, fontWeight: "700" },
  chartName: { color: "#64748b", fontSize: "0.9rem", marginTop: "4px" },
  chartPriceBlock: { textAlign: "right" },
  chartPrice: { color: "#f1f5f9", fontSize: "2rem", fontWeight: "700" },
  chartChange: { fontSize: "1rem", marginTop: "4px" },
  periodRow: { display: "flex", gap: "0.5rem", marginBottom: "1.5rem" },
  periodBtn: { padding: "0.4rem 1rem", borderRadius: "6px", border: "1px solid #334155", background: "#1e293b", color: "#64748b", fontSize: "0.9rem", cursor: "pointer" },
  periodActive: { background: "#3b82f6", color: "#fff", border: "1px solid #3b82f6" },
  chartWrap: { background: "#1e293b", borderRadius: "12px", padding: "1rem", marginBottom: "1.5rem" },
  chartLoading: { textAlign: "center", color: "#64748b", padding: "4rem", background: "#1e293b", borderRadius: "12px", marginBottom: "1.5rem" },
  statsRow: { display: "flex", gap: "1rem" },
  stat: { flex: 1, background: "#1e293b", borderRadius: "8px", padding: "1rem" },
  statLabel: { color: "#64748b", fontSize: "0.8rem", marginBottom: "4px" },
  statValue: { color: "#f1f5f9", fontSize: "1rem", fontWeight: "600" },
};