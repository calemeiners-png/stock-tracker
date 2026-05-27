import { useState, useEffect, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { supabase } from "./supabase";

const API = "https://stock-tracker-6acy.onrender.com";

function Auth() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSignUp, setIsSignUp] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (e) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <div style={styles.app}>
      <div style={{ ...styles.container, maxWidth: "400px" }}>
        <h1 style={styles.title}>📈 Stock Tracker</h1>
        <div style={styles.card}>
          <h2 style={styles.sectionTitle}>{isSignUp ? "Create Account" : "Sign In"}</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            <input style={styles.input} placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSubmit()} />
            <input style={styles.input} placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSubmit()} />
            {error && <p style={styles.error}>{error}</p>}
            <button style={styles.button} onClick={handleSubmit}>{loading ? "Loading..." : isSignUp ? "Create Account" : "Sign In"}</button>
            <button style={{ ...styles.button, background: "transparent", border: "1px solid #334155", color: "#94a3b8" }} onClick={() => setIsSignUp(!isSignUp)}>
              {isSignUp ? "Already have an account? Sign In" : "No account? Sign Up"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [tab, setTab] = useState("watchlist");
  const [scannerTab, setScannerTab] = useState("movers");
  const [ticker, setTicker] = useState("");
  const [stockData, setStockData] = useState(null);
  const [chartData, setChartData] = useState([]);
  const [chartPeriod, setChartPeriod] = useState("6mo");
  const [loadingChart, setLoadingChart] = useState(false);
  const [news, setNews] = useState([]);
  const [loadingNews, setLoadingNews] = useState(false);
  const [insiderTrades, setInsiderTrades] = useState([]);
  const [loadingInsider, setLoadingInsider] = useState(false);
  const [insiderFeed, setInsiderFeed] = useState([]);
  const [loadingFeed, setLoadingFeed] = useState(false);
  const [watchlist, setWatchlist] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [triggeredAlerts, setTriggeredAlerts] = useState([]);
  const [movers, setMovers] = useState([]);
  const [spikes, setSpikes] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [scanningSpikes, setScanningSpikes] = useState(false);
  const [lastScanned, setLastScanned] = useState(null);
  const [lastScannedSpikes, setLastScannedSpikes] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [alertTicker, setAlertTicker] = useState("");
  const [alertPrice, setAlertPrice] = useState("");
  const [alertDirection, setAlertDirection] = useState("above");
  const [directionFilter, setDirectionFilter] = useState("all");
  const [sectorFilter, setSectorFilter] = useState("all");
  const [spikeThreshold, setSpikeThreshold] = useState(3.0);

  const alertsRef = useRef(alerts);
  alertsRef.current = alerts;

  const SECTORS = {
    "Tech": ["AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META", "AMD", "INTC", "QCOM", "TXN", "MU", "AMAT", "LRCX", "KLAC", "MRVL", "SMCI", "ARM", "ASML", "CRM", "ADBE", "NOW", "SNOW", "PLTR", "DDOG", "NET", "CRWD", "ZS", "PANW", "OKTA", "MDB", "GTLB", "HUBS", "TEAM", "WDAY", "VEEV", "SHOP", "TWLO", "ZM", "DOCU", "BOX", "DOCN", "AVGO", "ORCL"],
    "Finance": ["JPM", "BAC", "GS", "MS", "WFC", "C", "BLK", "SCHW", "AXP", "V", "MA", "PYPL", "SQ", "COF", "USB", "PNC", "TFC", "BX", "KKR"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "OXY", "EOG", "PXD", "MPC", "VLO", "PSX", "HAL", "BKR", "DVN", "FANG", "APA", "HES"],
    "Health": ["JNJ", "PFE", "UNH", "ABBV", "MRK", "LLY", "BMY", "AMGN", "GILD", "BIIB", "REGN", "VRTX", "MRNA", "BNTX", "ILMN", "DXCM", "ISRG", "SYK", "MDT", "ABT", "TMO", "DHR", "A", "IDXX"],
    "Consumer": ["WMT", "HD", "MCD", "SBUX", "NKE", "TGT", "COST", "LOW", "TJX", "BABA", "JD", "PDD", "MELI", "SE", "GRAB", "DASH", "UBER", "LYFT", "ABNB", "BKNG", "EXPE", "MAR", "HLT"],
    "ETFs": ["SPY", "QQQ", "IWM", "DIA", "VTI", "VOO", "ARKK", "ARKW", "ARKG", "XLF", "XLK", "XLE", "XLV", "XLI", "XLB", "XLU", "XLP", "XLY", "GLD", "SLV", "USO", "TLT", "HYG", "LQD", "EEM", "VXX", "SQQQ", "TQQQ", "SPXU", "UVXY", "BITI", "BITO"],
    "Crypto": ["COIN", "MSTR", "RIOT", "MARA", "CLSK", "CIFR", "HUT"],
    "Auto & EV": ["TSLA", "F", "GM", "RIVN", "LCID", "NIO", "LI", "XPEV", "FSR"],
    "Defense": ["BA", "LMT", "RTX", "NOC", "GD", "HON", "GE", "CAT", "DE", "MMM"],
  };

  const getSector = (t) => {
    for (const [sector, tickers] of Object.entries(SECTORS)) {
      if (tickers.includes(t)) return sector;
    }
    return "Other";
  };

  const filteredMovers = movers.filter((s) => {
    const directionOk = directionFilter === "all" || s.direction === directionFilter;
    const sectorOk = sectorFilter === "all" || getSector(s.ticker) === sectorFilter;
    return directionOk && sectorOk;
  });

  const availableSectors = ["all", ...Object.keys(SECTORS), "Other"];

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });
    supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });
  }, []);

  useEffect(() => {
    if (!user) return;
    const loadWatchlist = async () => {
      const { data } = await supabase.from("watchlists").select("*").eq("user_id", user.id);
      if (data) setWatchlist(data);
    };
    const loadAlerts = async () => {
      const { data } = await supabase.from("alerts").select("*").eq("user_id", user.id);
      if (data) setAlerts(data);
    };
    loadWatchlist();
    loadAlerts();
  }, [user]);

  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  useEffect(() => {
    const checkAlerts = async () => {
      const currentAlerts = alertsRef.current;
      if (currentAlerts.length === 0) return;
      for (const alert of currentAlerts) {
        try {
          const res = await fetch(`${API}/stock/${alert.ticker}`);
          const data = await res.json();
          const price = data.price;
          if (!price) continue;
          const triggered =
            (alert.direction === "above" && price >= alert.target_price) ||
            (alert.direction === "below" && price <= alert.target_price);
          if (triggered) {
            if (Notification.permission === "granted") {
              new Notification(`🔔 ${alert.ticker} Alert!`, {
                body: `${alert.ticker} is now $${price.toFixed(2)} — your target of $${alert.target_price} was hit!`,
              });
            }
            setTriggeredAlerts((prev) => [...prev, { ...alert, currentPrice: price }]);
            await supabase.from("alerts").delete().eq("id", alert.id);
            setAlerts((prev) => prev.filter((a) => a.id !== alert.id));
          }
        } catch (e) {
          continue;
        }
      }
    };
    const interval = setInterval(checkAlerts, 60 * 1000);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchStock = async (symbol) => {
    setLoading(true);
    setError("");
    setChartData([]);
    setNews([]);
    setInsiderTrades([]);
    try {
      const res = await fetch(`${API}/stock/${symbol}`);
      const data = await res.json();
      if (data.detail) throw new Error(data.detail);
      setStockData(data);
      fetchChart(symbol, chartPeriod);
      fetchNews(symbol);
      fetchInsider(symbol);
    } catch (e) {
      setError("Could not find that ticker. Try again.");
    }
    setLoading(false);
  };

  const fetchChart = async (symbol, period) => {
    setLoadingChart(true);
    try {
      const res = await fetch(`${API}/chart/${symbol}?period=${period}`);
      const data = await res.json();
      setChartData(data.data || []);
    } catch (e) {
      setChartData([]);
    }
    setLoadingChart(false);
  };

  const fetchNews = async (symbol) => {
    setLoadingNews(true);
    try {
      const res = await fetch(`${API}/news/${symbol}`);
      const data = await res.json();
      setNews(data.articles || []);
    } catch (e) {
      setNews([]);
    }
    setLoadingNews(false);
  };

  const fetchInsider = async (symbol) => {
    setLoadingInsider(true);
    try {
      const res = await fetch(`${API}/insider/${symbol}`);
      const data = await res.json();
      setInsiderTrades(data.trades || []);
    } catch (e) {
      setInsiderTrades([]);
    }
    setLoadingInsider(false);
  };

  const fetchInsiderFeed = async () => {
    setLoadingFeed(true);
    try {
      const res = await fetch(`${API}/insider-feed`);
      const data = await res.json();
      setInsiderFeed(data.trades || []);
    } catch (e) {
      setInsiderFeed([]);
    }
    setLoadingFeed(false);
  };

  const scanMarket = async () => {
    setScanning(true);
    try {
      const res = await fetch(`${API}/scan`);
      const data = await res.json();
      setMovers(data.movers || []);
      setLastScanned(new Date().toLocaleTimeString());
    } catch (e) {
      setError("Scan failed.");
    }
    setScanning(false);
  };

  const scanVolumeSpikes = async (threshold = spikeThreshold) => {
    setScanningSpikes(true);
    try {
      const res = await fetch(`${API}/volume-spikes?threshold=${threshold}`);
      const data = await res.json();
      setSpikes(data.spikes || []);
      setLastScannedSpikes(new Date().toLocaleTimeString());
    } catch (e) {
      setError("Volume scan failed.");
    }
    setScanningSpikes(false);
  };

  useEffect(() => {
    if (tab !== "scanner") return;
    let interval;
    if (scannerTab === "movers" && lastScanned) {
      interval = setInterval(scanMarket, 5 * 60 * 1000);
    }
    if (scannerTab === "volume" && lastScannedSpikes) {
      interval = setInterval(scanVolumeSpikes, 5 * 60 * 1000);
    }
    return () => clearInterval(interval);
  }, [tab, scannerTab]); // eslint-disable-line react-hooks/exhaustive-deps

  const addToWatchlist = async () => {
    if (!stockData || watchlist.find((s) => s.ticker === stockData.ticker)) return;
    const newItem = {
      user_id: user.id,
      ticker: stockData.ticker,
      name: stockData.name,
      price: stockData.price,
      change_pct: stockData.change_pct,
    };
    const { data } = await supabase.from("watchlists").insert(newItem).select();
    if (data) setWatchlist([...watchlist, ...data]);
  };

  const removeFromWatchlist = async (id) => {
    await supabase.from("watchlists").delete().eq("id", id);
    setWatchlist(watchlist.filter((s) => s.id !== id));
  };

  const addAlert = async () => {
    if (!alertTicker || !alertPrice) return;
    const newAlert = {
      user_id: user.id,
      ticker: alertTicker.toUpperCase(),
      target_price: parseFloat(alertPrice),
      direction: alertDirection,
      created_at: new Date().toLocaleString(),
    };
    const { data } = await supabase.from("alerts").insert(newAlert).select();
    if (data) setAlerts([...alerts, ...data]);
    setAlertTicker("");
    setAlertPrice("");
  };

  const removeAlert = async (id) => {
    await supabase.from("alerts").delete().eq("id", id);
    setAlerts(alerts.filter((a) => a.id !== id));
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setWatchlist([]);
    setAlerts([]);
  };

  const formatPrice = (p) => (p ? `$${p.toFixed(2)}` : "N/A");
  const formatPct = (p) => (p != null ? `${p > 0 ? "+" : ""}${p.toFixed(2)}%` : "N/A");
  const formatVolume = (v) => (v ? v.toLocaleString() : "N/A");
  const formatCap = (c) => {
    if (!c) return "N/A";
    if (c >= 1e12) return `$${(c / 1e12).toFixed(2)}T`;
    if (c >= 1e9) return `$${(c / 1e9).toFixed(2)}B`;
    return `$${(c / 1e6).toFixed(2)}M`;
  };
  const formatShares = (s) => s ? s.toLocaleString() : "N/A";

  const isUp = chartData.length > 1 && chartData[chartData.length - 1].price >= chartData[0].price;
  const chartColor = isUp ? "#22c55e" : "#ef4444";
  const periods = ["1mo", "3mo", "6mo", "1y", "2y"];

  if (!user) return <Auth />;

  return (
    <div style={styles.app}>
      <div style={styles.container}>
        <div style={styles.topBar}>
          <h1 style={styles.title}>📈 Stock Tracker</h1>
          <div style={styles.userBar}>
            <span style={styles.userEmail}>{user.email}</span>
            <button style={styles.signOutBtn} onClick={handleSignOut}>Sign Out</button>
          </div>
        </div>

        {triggeredAlerts.map((a) => (
          <div key={a.id} style={styles.alertBanner}>
            🔔 <strong>{a.ticker}</strong> hit your target of ${a.target_price}! Current: ${a.currentPrice?.toFixed(2)}
            <button style={styles.dismissBtn} onClick={() => setTriggeredAlerts((prev) => prev.filter((t) => t.id !== a.id))}>✕</button>
          </div>
        ))}

        <div style={styles.tabs}>
          <button style={{ ...styles.tab, ...(tab === "watchlist" ? styles.tabActive : {}) }} onClick={() => setTab("watchlist")}>⭐ Watchlist</button>
          <button style={{ ...styles.tab, ...(tab === "scanner" ? styles.tabActive : {}) }} onClick={() => setTab("scanner")}>🔍 Scanner</button>
          <button style={{ ...styles.tab, ...(tab === "insider" ? styles.tabActive : {}) }} onClick={() => { setTab("insider"); if (insiderFeed.length === 0) fetchInsiderFeed(); }}>🏛️ Insider</button>
          <button style={{ ...styles.tab, ...(tab === "alerts" ? styles.tabActive : {}) }} onClick={() => setTab("alerts")}>
            🔔 Alerts {alerts.length > 0 && <span style={styles.badge}>{alerts.length}</span>}
          </button>
        </div>

        {/* WATCHLIST TAB */}
        {tab === "watchlist" && (
          <div>
            <div style={styles.searchBox}>
              <input style={styles.input} placeholder="Enter ticker (e.g. AAPL, TSLA, SPY)" value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} onKeyDown={(e) => e.key === "Enter" && fetchStock(ticker)} />
              <button style={styles.button} onClick={() => fetchStock(ticker)}>{loading ? "Loading..." : "Search"}</button>
            </div>

            {error && <p style={styles.error}>{error}</p>}

            {stockData && (
              <div style={styles.card}>
                <div style={styles.cardHeader}>
                  <div>
                    <h2 style={styles.stockName}>{stockData.name}</h2>
                    <span style={styles.tickerBadge}>{stockData.ticker}</span>
                  </div>
                  <div style={styles.priceBlock}>
                    <div style={styles.price}>{formatPrice(stockData.price)}</div>
                    <div style={{ ...styles.change, color: stockData.change_pct >= 0 ? "#22c55e" : "#ef4444" }}>
                      {stockData.change_pct >= 0 ? "▲" : "▼"} {formatPct(stockData.change_pct)} (52w)
                    </div>
                  </div>
                </div>
                <div style={styles.statsRow}>
                  <div style={styles.stat}><div style={styles.statLabel}>Volume</div><div style={styles.statValue}>{formatVolume(stockData.volume)}</div></div>
                  <div style={styles.stat}><div style={styles.statLabel}>Market Cap</div><div style={styles.statValue}>{formatCap(stockData.market_cap)}</div></div>
                </div>
                <div style={styles.periodRow}>
                  {periods.map((p) => (
                    <button key={p} style={{ ...styles.periodBtn, ...(chartPeriod === p ? styles.periodActive : {}) }} onClick={() => { setChartPeriod(p); fetchChart(stockData.ticker, p); }}>{p}</button>
                  ))}
                </div>
                {loadingChart && <div style={styles.chartLoading}>Loading chart...</div>}
                {!loadingChart && chartData.length > 0 && (
                  <div style={styles.chartWrap}>
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} interval={Math.floor(chartData.length / 5)} />
                        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} domain={["auto", "auto"]} tickFormatter={(v) => `$${v}`} width={60} />
                        <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} labelStyle={{ color: "#94a3b8" }} itemStyle={{ color: chartColor }} formatter={(v) => [`$${v}`, "Price"]} />
                        <Line type="monotone" dataKey="price" stroke={chartColor} strokeWidth={2} dot={false} activeDot={{ r: 4, fill: chartColor }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {loadingNews && <div style={styles.chartLoading}>Loading news...</div>}
                {!loadingNews && news.length > 0 && (
                  <div style={{ marginBottom: "1rem" }}>
                    <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.75rem" }}>Latest News</div>
                    {news.map((article, i) => (
                      <a key={i} href={article.url} target="_blank" rel="noreferrer" style={styles.newsItem}>
                        <div style={styles.newsHeadline}>{article.headline}</div>
                        <div style={styles.newsMeta}>{article.source} · {article.datetime}</div>
                      </a>
                    ))}
                  </div>
                )}

                {loadingInsider && <div style={styles.chartLoading}>Loading insider trades...</div>}
                {!loadingInsider && insiderTrades.length > 0 && (
                  <div style={{ marginBottom: "1rem" }}>
                    <div style={{ color: "#94a3b8", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.75rem" }}>Insider Trades</div>
                    {insiderTrades.map((t, i) => (
                      <div key={i} style={styles.insiderItem}>
                        <div>
                          <div style={styles.insiderName}>{t.name}</div>
                          <div style={styles.insiderMeta}>{t.title || "Insider"} · {t.date}</div>
                        </div>
                        <div style={styles.insiderRight}>
                          <div style={styles.insiderShares}>{formatShares(t.shares)} shares</div>
                          <span style={{ ...styles.insiderBadge, background: t.action === "buy" ? "#14532d" : "#450a0a", color: t.action === "buy" ? "#22c55e" : "#ef4444" }}>
                            {t.action === "buy" ? "▲ BUY" : "▼ SELL"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <button style={styles.addButton} onClick={addToWatchlist}>+ Add to Watchlist</button>
              </div>
            )}

            {watchlist.length === 0 && !stockData && <div style={styles.empty}>Search for a stock above and add it to your watchlist</div>}

            {watchlist.length > 0 && (
              <div style={styles.watchlist}>
                <h2 style={styles.sectionTitle}>Your Watchlist</h2>
                {watchlist.map((s) => (
                  <div key={s.id} style={styles.watchItem}>
                    <div>
                      <div style={styles.watchTicker}>{s.ticker}</div>
                      <div style={styles.watchName}>{s.name}</div>
                    </div>
                    <div style={styles.watchRight}>
                      <div style={styles.watchPrice}>{formatPrice(s.price)}</div>
                      <div style={{ color: s.change_pct >= 0 ? "#22c55e" : "#ef4444", fontSize: "0.85rem" }}>{formatPct(s.change_pct)}</div>
                      <button style={styles.addSmallBtn} onClick={() => fetchStock(s.ticker)}>Chart</button>
                      <button style={styles.removeBtn} onClick={() => removeFromWatchlist(s.id)}>✕</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* SCANNER TAB */}
        {tab === "scanner" && (
          <div>
            <div style={styles.scannerTabs}>
              <button style={{ ...styles.scannerTab, ...(scannerTab === "movers" ? styles.scannerTabActive : {}) }} onClick={() => setScannerTab("movers")}>📈 Price Movers</button>
              <button style={{ ...styles.scannerTab, ...(scannerTab === "volume" ? styles.scannerTabActive : {}) }} onClick={() => setScannerTab("volume")}>🔊 Volume Spikes</button>
            </div>

            {scannerTab === "movers" && (
              <div>
                <div style={styles.scanHeader}>
                  <div>
                    <p style={styles.scanInfo}>Scanning <strong style={{ color: "#f1f5f9" }}>200+ stocks</strong> for moves greater than 2%</p>
                    {lastScanned && <p style={styles.scanTime}>Last scanned: {lastScanned} · Auto-refreshes every 5 min</p>}
                  </div>
                  <button style={styles.button} onClick={scanMarket} disabled={scanning}>{scanning ? "Scanning..." : "🔍 Scan Now"}</button>
                </div>

                {movers.length > 0 && (
                  <div style={styles.filterSection}>
                    <div style={styles.filterGroup}>
                      <div style={styles.filterLabel}>Direction</div>
                      <div style={styles.filterRow}>
                        {["all", "up", "down"].map((d) => (
                          <button key={d} style={{ ...styles.filterBtn, ...(directionFilter === d ? { background: d === "up" ? "#22c55e" : d === "down" ? "#ef4444" : "#3b82f6", color: "#fff", border: "none" } : {}) }} onClick={() => setDirectionFilter(d)}>
                            {d === "all" ? "All" : d === "up" ? "▲ Up" : "▼ Down"}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div style={styles.filterGroup}>
                      <div style={styles.filterLabel}>Sector</div>
                      <div style={styles.filterRowWrap}>
                        {availableSectors.map((s) => (
                          <button key={s} style={{ ...styles.filterBtn, ...(sectorFilter === s ? { background: "#3b82f6", color: "#fff", border: "none" } : {}) }} onClick={() => setSectorFilter(s)}>
                            {s === "all" ? "All Sectors" : s}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {scanning && <div style={styles.scanning}>⏳ Scanning market... this takes 45-60 seconds</div>}
                {!scanning && movers.length === 0 && lastScanned && <div style={styles.empty}>No significant movers found right now.</div>}

                {filteredMovers.length > 0 && (
                  <div style={styles.watchlist}>
                    <h2 style={styles.sectionTitle}>
                      🔥 {filteredMovers.length} Movers
                      {directionFilter !== "all" && ` · ${directionFilter === "up" ? "▲ Up" : "▼ Down"}`}
                      {sectorFilter !== "all" && ` · ${sectorFilter}`}
                    </h2>
                    {filteredMovers.map((s) => (
                      <div key={s.ticker} style={styles.watchItem}>
                        <div>
                          <div style={styles.watchTicker}>{s.ticker}</div>
                          <div style={styles.watchName}>{s.name}</div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "2px" }}>{getSector(s.ticker)} · Volume: {s.volume_ratio}x avg</div>
                        </div>
                        <div style={styles.watchRight}>
                          <div style={styles.watchPrice}>${s.price}</div>
                          <div style={{ fontSize: "1rem", fontWeight: "700", color: s.direction === "up" ? "#22c55e" : "#ef4444" }}>
                            {s.direction === "up" ? "▲" : "▼"} {formatPct(s.change_pct)}
                          </div>
                          <button style={styles.addSmallBtn} onClick={() => { setStockData(s); fetchChart(s.ticker, chartPeriod); setTab("watchlist"); }}>Chart</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {!scanning && movers.length > 0 && filteredMovers.length === 0 && <div style={styles.empty}>No movers match your current filters.</div>}
              </div>
            )}

            {scannerTab === "volume" && (
              <div>
                <div style={styles.scanHeader}>
                  <div>
                    <p style={styles.scanInfo}>Scanning for stocks trading at <strong style={{ color: "#f1f5f9" }}>{spikeThreshold}x+ normal volume</strong></p>
                    {lastScannedSpikes && <p style={styles.scanTime}>Last scanned: {lastScannedSpikes} · Auto-refreshes every 5 min</p>}
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", alignItems: "flex-end" }}>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      {[1.5, 2, 3, 5].map((t) => (
                        <button key={t} style={{ ...styles.filterBtn, ...(spikeThreshold === t ? { background: "#f59e0b", color: "#000", border: "none" } : {}) }} onClick={() => { setSpikeThreshold(t); scanVolumeSpikes(t); }}>
                          {t}x
                        </button>
                      ))}
                    </div>
                    <button style={styles.button} onClick={() => scanVolumeSpikes(spikeThreshold)} disabled={scanningSpikes}>{scanningSpikes ? "Scanning..." : "🔊 Scan Now"}</button>
                  </div>
                </div>

                {scanningSpikes && <div style={styles.scanning}>⏳ Scanning for volume spikes... this takes about 30 seconds</div>}
                {!scanningSpikes && spikes.length === 0 && lastScannedSpikes && <div style={styles.empty}>No volume spikes found right now.</div>}

                {spikes.length > 0 && (
                  <div style={styles.watchlist}>
                    <h2 style={styles.sectionTitle}>🔊 {spikes.length} Volume Spikes</h2>
                    {spikes.map((s) => (
                      <div key={s.ticker} style={styles.watchItem}>
                        <div>
                          <div style={styles.watchTicker}>{s.ticker}</div>
                          <div style={styles.watchName}>{s.name}</div>
                          <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "2px" }}>
                            {getSector(s.ticker)} · Vol: {s.volume.toLocaleString()} vs avg {s.avg_volume.toLocaleString()}
                          </div>
                        </div>
                        <div style={styles.watchRight}>
                          <div style={styles.watchPrice}>${s.price}</div>
                          <div style={{ fontSize: "0.9rem", fontWeight: "700", color: "#f59e0b" }}>🔊 {s.volume_ratio}x</div>
                          <div style={{ fontSize: "0.85rem", color: s.direction === "up" ? "#22c55e" : "#ef4444" }}>
                            {s.direction === "up" ? "▲" : "▼"} {formatPct(s.change_pct)}
                          </div>
                          <button style={styles.addSmallBtn} onClick={() => { setStockData(s); fetchChart(s.ticker, chartPeriod); setTab("watchlist"); }}>Chart</button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* INSIDER TAB */}
        {tab === "insider" && (
          <div>
            <div style={styles.scanHeader}>
              <div>
                <p style={styles.scanInfo}>Recent trades by <strong style={{ color: "#f1f5f9" }}>corporate insiders</strong> across major stocks</p>
                <p style={styles.scanTime}>Data from SEC filings via Finnhub</p>
              </div>
              <button style={styles.button} onClick={fetchInsiderFeed} disabled={loadingFeed}>
                {loadingFeed ? "Loading..." : "🔄 Refresh"}
              </button>
            </div>

            {loadingFeed && <div style={styles.scanning}>⏳ Loading insider trades...</div>}

            {!loadingFeed && insiderFeed.length === 0 && (
              <div style={styles.empty}>No insider trades found. Click Refresh to load.</div>
            )}

            {insiderFeed.length > 0 && (
              <div style={styles.watchlist}>
                <h2 style={styles.sectionTitle}>🏛️ {insiderFeed.length} Recent Insider Trades</h2>
                {insiderFeed.map((t, i) => (
                  <div key={i} style={styles.watchItem}>
                    <div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <div style={styles.watchTicker}>{t.ticker}</div>
                        <span style={{ ...styles.insiderBadge, background: t.action === "buy" ? "#14532d" : "#450a0a", color: t.action === "buy" ? "#22c55e" : "#ef4444" }}>
                          {t.action === "buy" ? "▲ BUY" : "▼ SELL"}
                        </span>
                      </div>
                      <div style={styles.insiderName}>{t.name}</div>
                      <div style={styles.insiderMeta}>{t.title || "Insider"} · {t.date}</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={styles.insiderShares}>{formatShares(t.shares)} shares</div>
                      <button style={{ ...styles.addSmallBtn, marginTop: "4px" }} onClick={() => { fetchStock(t.ticker); setTab("watchlist"); }}>
                        Chart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ALERTS TAB */}
        {tab === "alerts" && (
          <div>
            <div style={styles.card}>
              <h2 style={styles.sectionTitle}>🔔 Set a Price Alert</h2>
              <div style={styles.alertForm}>
                <input style={styles.input} placeholder="Ticker (e.g. AAPL)" value={alertTicker} onChange={(e) => setAlertTicker(e.target.value.toUpperCase())} />
                <select style={styles.select} value={alertDirection} onChange={(e) => setAlertDirection(e.target.value)}>
                  <option value="above">Goes above</option>
                  <option value="below">Goes below</option>
                </select>
                <input style={styles.input} placeholder="Target price (e.g. 200)" type="number" value={alertPrice} onChange={(e) => setAlertPrice(e.target.value)} />
                <button style={styles.button} onClick={addAlert}>+ Add Alert</button>
              </div>
              <p style={styles.scanTime}>Alerts check every 60 seconds. Allow browser notifications when prompted.</p>
            </div>

            {alerts.length === 0 && <div style={styles.empty}>No alerts set yet. Add one above!</div>}

            {alerts.length > 0 && (
              <div style={styles.watchlist}>
                <h2 style={styles.sectionTitle}>Active Alerts</h2>
                {alerts.map((a) => (
                  <div key={a.id} style={styles.watchItem}>
                    <div>
                      <div style={styles.watchTicker}>{a.ticker}</div>
                      <div style={styles.watchName}>Notify when price goes <strong>{a.direction}</strong> ${a.target_price}</div>
                      <div style={{ fontSize: "0.75rem", color: "#64748b" }}>Set: {a.created_at}</div>
                    </div>
                    <button style={styles.removeBtn} onClick={() => removeAlert(a.id)}>✕</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  app: { minHeight: "100vh", background: "#0f172a", padding: "2rem 1rem" },
  container: { maxWidth: "700px", margin: "0 auto" },
  topBar: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" },
  title: { color: "#f1f5f9", fontSize: "2rem", margin: 0 },
  userBar: { display: "flex", alignItems: "center", gap: "1rem" },
  userEmail: { color: "#64748b", fontSize: "0.85rem" },
  signOutBtn: { padding: "0.4rem 0.75rem", borderRadius: "6px", border: "1px solid #334155", background: "transparent", color: "#94a3b8", fontSize: "0.85rem", cursor: "pointer" },
  tabs: { display: "flex", gap: "0.5rem", marginBottom: "1.5rem" },
  tab: { flex: 1, padding: "0.75rem", borderRadius: "8px", border: "1px solid #334155", background: "#1e293b", color: "#94a3b8", fontSize: "0.9rem", cursor: "pointer" },
  tabActive: { background: "#3b82f6", color: "#fff", border: "1px solid #3b82f6" },
  badge: { background: "#ef4444", color: "#fff", borderRadius: "999px", padding: "1px 7px", fontSize: "0.75rem", marginLeft: "6px" },
  scannerTabs: { display: "flex", gap: "0.5rem", marginBottom: "1.5rem" },
  scannerTab: { flex: 1, padding: "0.65rem", borderRadius: "8px", border: "1px solid #334155", background: "#1e293b", color: "#94a3b8", fontSize: "0.95rem", cursor: "pointer" },
  scannerTabActive: { background: "#1d4ed8", color: "#fff", border: "1px solid #1d4ed8" },
  searchBox: { display: "flex", gap: "0.5rem", marginBottom: "1rem" },
  input: { flex: 1, padding: "0.75rem 1rem", borderRadius: "8px", border: "1px solid #334155", background: "#1e293b", color: "#f1f5f9", fontSize: "1rem", outline: "none" },
  select: { padding: "0.75rem 1rem", borderRadius: "8px", border: "1px solid #334155", background: "#1e293b", color: "#f1f5f9", fontSize: "1rem" },
  button: { padding: "0.75rem 1.5rem", borderRadius: "8px", border: "none", background: "#3b82f6", color: "#fff", fontSize: "1rem", cursor: "pointer", fontWeight: "600" },
  error: { color: "#ef4444", marginBottom: "1rem" },
  card: { background: "#1e293b", borderRadius: "12px", padding: "1.5rem", marginBottom: "1.5rem", border: "1px solid #334155" },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" },
  stockName: { color: "#f1f5f9", fontSize: "1.25rem", margin: 0 },
  tickerBadge: { background: "#334155", color: "#94a3b8", padding: "2px 8px", borderRadius: "4px", fontSize: "0.85rem" },
  priceBlock: { textAlign: "right" },
  price: { color: "#f1f5f9", fontSize: "1.75rem", fontWeight: "700" },
  change: { fontSize: "0.9rem", marginTop: "2px" },
  statsRow: { display: "flex", gap: "1rem", marginBottom: "1rem" },
  stat: { flex: 1, background: "#0f172a", borderRadius: "8px", padding: "0.75rem" },
  statLabel: { color: "#64748b", fontSize: "0.8rem", marginBottom: "4px" },
  statValue: { color: "#f1f5f9", fontSize: "1rem", fontWeight: "600" },
  addButton: { width: "100%", padding: "0.65rem", borderRadius: "8px", border: "none", background: "#22c55e", color: "#fff", fontSize: "1rem", cursor: "pointer", fontWeight: "600" },
  addSmallBtn: { padding: "0.4rem 0.75rem", borderRadius: "6px", border: "none", background: "#3b82f6", color: "#fff", fontSize: "0.8rem", cursor: "pointer", fontWeight: "600" },
  watchlist: { background: "#1e293b", borderRadius: "12px", padding: "1.5rem", border: "1px solid #334155" },
  sectionTitle: { color: "#f1f5f9", fontSize: "1.25rem", marginBottom: "1rem", marginTop: 0 },
  watchItem: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem 0", borderBottom: "1px solid #334155" },
  watchTicker: { color: "#f1f5f9", fontWeight: "700", fontSize: "1rem" },
  watchName: { color: "#64748b", fontSize: "0.85rem" },
  watchRight: { display: "flex", alignItems: "center", gap: "1rem" },
  watchPrice: { color: "#f1f5f9", fontWeight: "600" },
  removeBtn: { background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: "1rem" },
  empty: { textAlign: "center", color: "#64748b", padding: "3rem 0", fontSize: "1rem" },
  scanHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" },
  scanInfo: { color: "#94a3b8", margin: 0, fontSize: "0.95rem" },
  scanTime: { color: "#64748b", margin: "4px 0 0 0", fontSize: "0.8rem" },
  scanning: { textAlign: "center", color: "#94a3b8", padding: "2rem", background: "#1e293b", borderRadius: "12px", fontSize: "1rem" },
  alertBanner: { background: "#854d0e", color: "#fef08a", padding: "0.75rem 1rem", borderRadius: "8px", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" },
  dismissBtn: { marginLeft: "auto", background: "none", border: "none", color: "#fef08a", cursor: "pointer", fontSize: "1rem" },
  alertForm: { display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "0.75rem" },
  periodRow: { display: "flex", gap: "0.5rem", marginBottom: "1rem" },
  periodBtn: { padding: "0.35rem 0.75rem", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#64748b", fontSize: "0.85rem", cursor: "pointer" },
  periodActive: { background: "#3b82f6", color: "#fff", border: "1px solid #3b82f6" },
  chartWrap: { background: "#0f172a", borderRadius: "8px", padding: "1rem", marginBottom: "1rem" },
  chartLoading: { textAlign: "center", color: "#64748b", padding: "2rem", background: "#0f172a", borderRadius: "8px", marginBottom: "1rem" },
  filterSection: { background: "#1e293b", borderRadius: "12px", padding: "1rem", marginBottom: "1rem", border: "1px solid #334155" },
  filterGroup: { marginBottom: "0.75rem" },
  filterLabel: { color: "#64748b", fontSize: "0.8rem", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.05em" },
  filterRow: { display: "flex", gap: "0.5rem" },
  filterRowWrap: { display: "flex", gap: "0.5rem", flexWrap: "wrap" },
  filterBtn: { padding: "0.35rem 0.75rem", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#94a3b8", fontSize: "0.85rem", cursor: "pointer" },
  newsItem: { display: "block", padding: "0.75rem", background: "#0f172a", borderRadius: "8px", marginBottom: "0.5rem", textDecoration: "none", cursor: "pointer", border: "1px solid #334155" },
  newsHeadline: { color: "#f1f5f9", fontSize: "0.9rem", marginBottom: "4px", lineHeight: "1.4" },
  newsMeta: { color: "#64748b", fontSize: "0.75rem" },
  insiderItem: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.75rem", background: "#0f172a", borderRadius: "8px", marginBottom: "0.5rem", border: "1px solid #334155" },
  insiderName: { color: "#f1f5f9", fontSize: "0.9rem", fontWeight: "500" },
  insiderMeta: { color: "#64748b", fontSize: "0.75rem", marginTop: "2px" },
  insiderRight: { display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "4px" },
  insiderShares: { color: "#94a3b8", fontSize: "0.85rem" },
  insiderBadge: { padding: "2px 8px", borderRadius: "4px", fontSize: "0.75rem", fontWeight: "700" },
};

export default App;