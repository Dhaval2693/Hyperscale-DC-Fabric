import { useEffect, useState, useRef } from "react";

const C = {
  bg: "#0f172a",
  card: "#1e293b",
  border: "#334155",
  text: "#f1f5f9",
  muted: "#94a3b8",
  dim: "#475569",
  downlink: "#10b981",
  uplink: "#6366f1",
  packet: "#f43f5e",
  idle: "#1e293b",
  active: "#f59e0b",
  switch: "#06b6d4",
};

const NUM_DOWN = 32;
const NUM_UP = 16;
const SPEED_MS = 120;

function useTraffic(active: boolean, numDown: number, numUp: number, rate: number) {
  const [activeDown, setActiveDown] = useState<Set<number>>(new Set());
  const [activeUp, setActiveUp] = useState<boolean>(false);
  const frameRef = useRef(0);

  useEffect(() => {
    if (!active) { setActiveDown(new Set()); setActiveUp(false); return; }
    const interval = setInterval(() => {
      frameRef.current++;
      const newActive = new Set<number>();
      const numActive = Math.round(numDown * rate);
      const shuffled = Array.from({ length: numDown }, (_, i) => i)
        .sort(() => Math.random() - 0.5)
        .slice(0, numActive + Math.floor(Math.sin(frameRef.current * 0.3) * 4));
      shuffled.forEach(i => newActive.add(i));
      setActiveDown(newActive);
      setActiveUp(newActive.size > 0);
    }, SPEED_MS);
    return () => clearInterval(interval);
  }, [active, numDown, numUp, rate]);

  return { activeDown, activeUp };
}

function PortGrid({ count, active, color, idleColor, label, cols = 8 }: {
  count: number; active: Set<number>; color: string; idleColor: string; label: string; cols?: number;
}) {
  const rows = Math.ceil(count / cols);
  return (
    <div>
      <div style={{ color: C.muted, fontSize: 11, fontWeight: 600, marginBottom: 6, letterSpacing: "0.05em" }}>{label}</div>
      <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 3 }}>
        {Array.from({ length: count }, (_, i) => (
          <div key={i} style={{
            width: 18, height: 18, borderRadius: 3,
            background: active.has(i) ? color : idleColor,
            border: `1px solid ${active.has(i) ? color : C.border}`,
            transition: "background 0.1s, border-color 0.1s",
            boxShadow: active.has(i) ? `0 0 6px ${color}66` : "none",
          }} />
        ))}
      </div>
      <div style={{ color: C.muted, fontSize: 10, marginTop: 4 }}>
        {active.size} / {count} active
      </div>
    </div>
  );
}

function BandwidthBar({ used, total, color, label }: {
  used: number; total: number; color: string; label: string;
}) {
  const pct = Math.min(used / total, 1);
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ color: C.muted, fontSize: 11 }}>{label}</span>
        <span style={{ color: C.text, fontSize: 11, fontWeight: 600 }}>
          {Math.round(used * 25)} / {total * 25} Gbps
        </span>
      </div>
      <div style={{ background: C.border, borderRadius: 4, height: 10, overflow: "hidden" }}>
        <div style={{
          width: `${pct * 100}%`, height: "100%", borderRadius: 4,
          background: color, transition: "width 0.15s",
          boxShadow: `0 0 8px ${color}88`
        }} />
      </div>
    </div>
  );
}

export function OversubscriptionRatio() {
  const [running, setRunning] = useState(false);
  const [mode, setMode] = useState<"cloud" | "ai">("cloud");

  const rate = mode === "cloud" ? 0.35 : 0.95;
  const { activeDown, activeUp } = useTraffic(running, NUM_DOWN, NUM_UP, rate);

  const downBw = activeDown.size;
  const upBw = activeUp ? Math.min(activeDown.size / 2, NUM_UP) : 0;
  const congested = downBw > NUM_UP * 2;

  return (
    <div style={{ background: C.bg, minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "28px 32px", fontFamily: "system-ui, sans-serif" }}>
      <h2 style={{ color: C.text, fontSize: 20, fontWeight: 800, marginBottom: 4, textAlign: "center" }}>
        Oversubscription Ratio
      </h2>
      <p style={{ color: C.muted, fontSize: 13, marginBottom: 20, textAlign: "center", maxWidth: 540 }}>
        A 48-port switch: 32 downlinks to servers × 25G = <strong style={{ color: C.downlink }}>800 Gbps</strong> downlink capacity.
        16 uplinks × 25G = <strong style={{ color: C.uplink }}>400 Gbps</strong> uplink — a <strong style={{ color: C.active }}>2:1 oversubscription</strong>.
      </p>

      <div style={{ display: "flex", gap: 24, alignItems: "flex-start", flexWrap: "wrap", justifyContent: "center" }}>

        {/* Switch Diagram */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20, minWidth: 300 }}>
          <div style={{ textAlign: "center", marginBottom: 16 }}>
            <div style={{ color: C.switch, fontSize: 13, fontWeight: 700, letterSpacing: "0.05em" }}>LEAF SWITCH</div>
            <div style={{ color: C.muted, fontSize: 11 }}>48-port, 25G</div>
          </div>

          {/* Uplinks at top */}
          <PortGrid count={NUM_UP} active={activeUp ? new Set(Array.from({ length: Math.round(upBw) }, (_, i) => i)) : new Set()} color={C.uplink} idleColor={C.idle} label="▲ UPLINKS (×16) → Spine" cols={8} />

          {/* Switch body */}
          <div style={{ background: `${C.switch}22`, border: `1px solid ${C.switch}44`, borderRadius: 8, padding: "10px 0", textAlign: "center", margin: "12px 0" }}>
            <span style={{ color: C.switch, fontSize: 13, fontWeight: 700 }}>FORWARDING ENGINE</span>
          </div>

          {/* Downlinks at bottom */}
          <PortGrid count={NUM_DOWN} active={activeDown} color={C.downlink} idleColor={C.idle} label="▼ DOWNLINKS (×32) → Servers" cols={8} />
        </div>

        {/* Stats & Controls */}
        <div style={{ minWidth: 260 }}>
          <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 18, marginBottom: 16 }}>
            <div style={{ color: C.text, fontSize: 13, fontWeight: 700, marginBottom: 12 }}>Live Bandwidth</div>
            <BandwidthBar used={downBw} total={NUM_DOWN} color={C.downlink} label="Downlink utilization" />
            <BandwidthBar used={upBw} total={NUM_UP} color={C.uplink} label="Uplink utilization" />

            {congested && (
              <div style={{ background: "#ef444422", border: "1px solid #ef4444", borderRadius: 6, padding: "8px 10px", marginTop: 10 }}>
                <div style={{ color: "#ef4444", fontSize: 12, fontWeight: 700 }}>⚠ CONGESTION</div>
                <div style={{ color: C.muted, fontSize: 11 }}>Downlink demand exceeds uplink capacity</div>
              </div>
            )}

            {!congested && running && (
              <div style={{ background: "#10b98122", border: "1px solid #10b981", borderRadius: 6, padding: "8px 10px", marginTop: 10 }}>
                <div style={{ color: C.downlink, fontSize: 12, fontWeight: 700 }}>✓ STATISTICAL MULTIPLEXING</div>
                <div style={{ color: C.muted, fontSize: 11 }}>Not all servers transmit simultaneously</div>
              </div>
            )}
          </div>

          {/* Mode selector */}
          <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 18, marginBottom: 16 }}>
            <div style={{ color: C.text, fontSize: 13, fontWeight: 700, marginBottom: 10 }}>Workload Type</div>
            <div style={{ display: "flex", gap: 8 }}>
              {(["cloud", "ai"] as const).map(m => (
                <button key={m} onClick={() => setMode(m)} style={{
                  flex: 1, padding: "8px 0", borderRadius: 8, border: "none", cursor: "pointer",
                  background: mode === m ? (m === "ai" ? C.packet : C.uplink) : C.border,
                  color: mode === m ? C.text : C.muted, fontSize: 12, fontWeight: 600,
                  transition: "all 0.2s"
                }}>
                  {m === "cloud" ? "☁ Web/Cloud" : "⚡ AI Training"}
                </button>
              ))}
            </div>
            <p style={{ color: C.muted, fontSize: 11, marginTop: 8, lineHeight: 1.5 }}>
              {mode === "cloud"
                ? "Statistical multiplexing works — servers rarely all burst at once (~35% active)"
                : "AI all-reduce: nearly all servers transmit simultaneously (~95% active) — oversubscription breaks down"}
            </p>
          </div>

          <button onClick={() => setRunning(r => !r)} style={{
            width: "100%", padding: "12px 0", borderRadius: 10, border: "none",
            background: running ? "#ef444444" : `${C.downlink}33`,
            color: running ? "#ef4444" : C.downlink, fontSize: 14, fontWeight: 700,
            cursor: "pointer", border: `1px solid ${running ? "#ef4444" : C.downlink}`,
            transition: "all 0.2s"
          }}>
            {running ? "■ Stop Simulation" : "▶ Start Simulation"}
          </button>
        </div>
      </div>

      {/* Ratio callout */}
      <div style={{ display: "flex", gap: 16, marginTop: 20 }}>
        {[
          { label: "Downlink", value: "800 Gbps", sub: "32 × 25G", color: C.downlink },
          { label: "Oversubscription", value: "2 : 1", sub: "downlink ÷ uplink", color: C.active },
          { label: "Uplink", value: "400 Gbps", sub: "16 × 25G", color: C.uplink },
        ].map(({ label, value, sub, color }) => (
          <div key={label} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 10, padding: "12px 20px", textAlign: "center" }}>
            <div style={{ color, fontSize: 20, fontWeight: 800 }}>{value}</div>
            <div style={{ color: C.text, fontSize: 12, fontWeight: 600 }}>{label}</div>
            <div style={{ color: C.muted, fontSize: 11 }}>{sub}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
