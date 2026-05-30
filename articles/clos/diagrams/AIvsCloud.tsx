import { useEffect, useState, useRef } from "react";

const C = {
  bg: "#0f172a",
  card: "#1e293b",
  border: "#334155",
  text: "#f1f5f9",
  muted: "#94a3b8",
  dim: "#475569",
  spine: "#6366f1",
  leaf: "#06b6d4",
  server: "#10b981",
  gpu: "#f43f5e",
  packet: "#f59e0b",
  aiPacket: "#a855f7",
  link: "#334155",
  linkActive: "#f59e0b",
  linkAI: "#a855f7",
};

interface Packet { id: number; from: number; to: number; t: number; color: string }

function lerp(a: number, b: number, t: number) { return a + (b - a) * t; }

function NetworkDiagram({ mode, w = 380, h = 340 }: { mode: "cloud" | "ai"; w?: number; h?: number }) {
  const spineY = 60;
  const leafY = 160;
  const serverY = 280;

  const numSpines = mode === "cloud" ? 3 : 2;
  const numLeaves = mode === "cloud" ? 2 : 2;
  const numServers = 6;

  const spineXs = Array.from({ length: numSpines }, (_, i) =>
    (w / (numSpines + 1)) * (i + 1));
  const leafXs = Array.from({ length: numLeaves }, (_, i) =>
    (w / (numLeaves + 1)) * (i + 1));
  const serverXs = Array.from({ length: numServers }, (_, i) =>
    (w / (numServers + 1)) * (i + 1));

  const [packets, setPackets] = useState<Packet[]>([]);
  const nextId = useRef(0);
  const animRef = useRef<number>();

  const isAI = mode === "ai";
  const linkColor = isAI ? C.linkAI : C.linkActive;

  useEffect(() => {
    let lastSpawn = 0;
    const spawnInterval = isAI ? 120 : 400;
    let prev: number;

    const loop = (ts: number) => {
      const dt = prev ? (ts - prev) / 1000 : 0;
      prev = ts;

      setPackets(pkts => {
        let next = pkts
          .map(p => ({ ...p, t: p.t + dt * (isAI ? 1.4 : 1.0) }))
          .filter(p => p.t < 1);

        if (ts - lastSpawn > spawnInterval) {
          lastSpawn = ts;
          if (isAI) {
            // All-reduce: many servers to many servers (east-west)
            const numNew = 4 + Math.floor(Math.random() * 3);
            for (let i = 0; i < numNew; i++) {
              const from = Math.floor(Math.random() * numServers);
              const to = (from + 1 + Math.floor(Math.random() * (numServers - 1))) % numServers;
              next.push({ id: nextId.current++, from, to, t: 0, color: C.aiPacket });
            }
          } else {
            // North-south: 1-2 servers active
            const numNew = 1 + Math.floor(Math.random() * 2);
            for (let i = 0; i < numNew; i++) {
              const from = Math.floor(Math.random() * numServers);
              next.push({ id: nextId.current++, from, to: -1, t: 0, color: C.packet });
            }
          }
        }
        return next.slice(-60);
      });

      animRef.current = requestAnimationFrame(loop);
    };

    animRef.current = requestAnimationFrame(loop);
    return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
  }, [isAI, mode]);

  function getPacketPos(p: Packet): { x: number; y: number } {
    const sx = serverXs[p.from];
    if (p.to === -1) {
      // North-south: server → leaf → spine
      const lx = leafXs[p.from < numServers / 2 ? 0 : 1];
      const spx = spineXs[Math.floor(Math.random() * numSpines)];
      if (p.t < 0.4) {
        const t2 = p.t / 0.4;
        return { x: lerp(sx, lx, t2), y: lerp(serverY, leafY, t2) };
      } else if (p.t < 0.8) {
        const t2 = (p.t - 0.4) / 0.4;
        return { x: lerp(lx, spx, t2), y: lerp(leafY, spineY, t2) };
      } else {
        const t2 = (p.t - 0.8) / 0.2;
        return { x: lerp(spx, spx, t2), y: lerp(spineY, spineY - 10, t2) };
      }
    } else {
      // East-west: server → leaf → spine → leaf → server (all-reduce)
      const tx = serverXs[p.to];
      const lx1 = leafXs[p.from < numServers / 2 ? 0 : 1];
      const lx2 = leafXs[p.to < numServers / 2 ? 0 : 1];
      const spx = spineXs[0];
      if (p.t < 0.25) {
        const t2 = p.t / 0.25;
        return { x: lerp(sx, lx1, t2), y: lerp(serverY, leafY, t2) };
      } else if (p.t < 0.5) {
        const t2 = (p.t - 0.25) / 0.25;
        return { x: lerp(lx1, spx, t2), y: lerp(leafY, spineY, t2) };
      } else if (p.t < 0.75) {
        const t2 = (p.t - 0.5) / 0.25;
        return { x: lerp(spx, lx2, t2), y: lerp(spineY, leafY, t2) };
      } else {
        const t2 = (p.t - 0.75) / 0.25;
        return { x: lerp(lx2, tx, t2), y: lerp(leafY, serverY, t2) };
      }
    }
  }

  const activeServers = new Set(packets.map(p => p.from));

  return (
    <svg width={w} height={h} style={{ overflow: "visible" }}>
      {/* Spine–Leaf links */}
      {spineXs.flatMap(sx =>
        leafXs.map((lx, li) => (
          <line key={`sl${sx}${li}`} x1={sx} y1={spineY + 16} x2={lx} y2={leafY - 16}
            stroke={C.link} strokeWidth={1.5} strokeOpacity={0.5} />
        ))
      )}
      {/* Leaf–Server links */}
      {leafXs.flatMap((lx, li) =>
        serverXs.slice(li * (numServers / numLeaves), (li + 1) * (numServers / numLeaves)).map((sx, si) => (
          <line key={`ls${li}${si}`} x1={lx} y1={leafY + 16} x2={sx} y2={serverY - 14}
            stroke={C.link} strokeWidth={1.5} strokeOpacity={0.5} />
        ))
      )}

      {/* Spine nodes */}
      {spineXs.map((sx, i) => (
        <g key={i}>
          <rect x={sx - 30} y={spineY - 16} width={60} height={32} rx={5}
            fill={C.spine} fillOpacity={0.15} stroke={C.spine} strokeWidth={1.5} />
          <text x={sx} y={spineY - 1} textAnchor="middle" fill={C.text} fontSize={10} fontWeight={700}>Spine</text>
          <text x={sx} y={spineY + 11} textAnchor="middle" fill={C.muted} fontSize={9}>S{i + 1}</text>
        </g>
      ))}

      {/* Leaf nodes */}
      {leafXs.map((lx, i) => (
        <g key={i}>
          <rect x={lx - 30} y={leafY - 16} width={60} height={32} rx={5}
            fill={C.leaf} fillOpacity={0.15} stroke={C.leaf} strokeWidth={1.5} />
          <text x={lx} y={leafY - 1} textAnchor="middle" fill={C.text} fontSize={10} fontWeight={700}>Leaf</text>
          <text x={lx} y={leafY + 11} textAnchor="middle" fill={C.muted} fontSize={9}>L{i + 1}</text>
        </g>
      ))}

      {/* Server/GPU nodes */}
      {serverXs.map((sx, i) => {
        const isActive = activeServers.has(i);
        const color = isAI ? C.gpu : C.server;
        return (
          <g key={i}>
            <rect x={sx - 22} y={serverY - 14} width={44} height={28} rx={5}
              fill={isActive ? color : C.card}
              stroke={isActive ? color : C.border}
              strokeWidth={isActive ? 2 : 1}
              style={{ transition: "fill 0.1s, stroke 0.1s" }} />
            <text x={sx} y={serverY - 2} textAnchor="middle"
              fill={isActive ? C.text : C.muted} fontSize={9} fontWeight={700}>
              {isAI ? "GPU" : "SRV"}
            </text>
            <text x={sx} y={serverY + 9} textAnchor="middle"
              fill={isActive ? C.text : C.dim} fontSize={8}>{i + 1}</text>
          </g>
        );
      })}

      {/* Packets */}
      {packets.map(p => {
        const pos = getPacketPos(p);
        return (
          <circle key={p.id} cx={pos.x} cy={pos.y} r={4}
            fill={p.color} opacity={0.9}
            style={{ filter: `drop-shadow(0 0 4px ${p.color})` }} />
        );
      })}

      {/* Active count */}
      <text x={w / 2} y={h - 5} textAnchor="middle" fill={C.muted} fontSize={10}>
        {activeServers.size}/{numServers} {isAI ? "GPUs" : "servers"} active
      </text>
    </svg>
  );
}

export function AIvsCloud() {
  return (
    <div style={{ background: C.bg, minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "24px 28px", fontFamily: "system-ui, sans-serif" }}>
      <h2 style={{ color: C.text, fontSize: 20, fontWeight: 800, marginBottom: 4, textAlign: "center" }}>
        Cloud Fabric vs AI Training Fabric
      </h2>
      <p style={{ color: C.muted, fontSize: 13, marginBottom: 24, textAlign: "center", maxWidth: 600 }}>
        Same Clos topology — different traffic patterns. Cloud relies on statistical multiplexing;
        AI all-reduce saturates all links simultaneously.
      </p>

      <div style={{ display: "flex", gap: 32, alignItems: "flex-start", flexWrap: "wrap", justifyContent: "center" }}>
        {/* Cloud panel */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 14, padding: "20px 24px", minWidth: 340 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: C.packet }} />
            <span style={{ color: C.text, fontSize: 15, fontWeight: 700 }}>Cloud / Web Workload</span>
          </div>
          <p style={{ color: C.muted, fontSize: 11, marginBottom: 14, lineHeight: 1.5 }}>
            North-south dominant. Statistical multiplexing holds.
            2:1 oversubscription works — low cost per server.
          </p>
          <NetworkDiagram mode="cloud" w={340} h={320} />
          <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
            {[
              { label: "Oversubscription", value: "2:1", color: C.packet },
              { label: "Traffic pattern", value: "N-S sporadic", color: C.muted },
              { label: "Congestion risk", value: "Low", color: C.server },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 10px", flex: 1 }}>
                <div style={{ color, fontSize: 12, fontWeight: 700 }}>{value}</div>
                <div style={{ color: C.muted, fontSize: 10 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* AI panel */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 14, padding: "20px 24px", minWidth: 340 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
            <div style={{ width: 10, height: 10, borderRadius: "50%", background: C.aiPacket }} />
            <span style={{ color: C.text, fontSize: 15, fontWeight: 700 }}>AI Training Workload</span>
          </div>
          <p style={{ color: C.muted, fontSize: 11, marginBottom: 14, lineHeight: 1.5 }}>
            All-reduce: every GPU communicates with every GPU simultaneously.
            East-west floods the fabric — non-blocking design required.
          </p>
          <NetworkDiagram mode="ai" w={340} h={320} />
          <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
            {[
              { label: "Oversubscription", value: "1:1", color: C.aiPacket },
              { label: "Traffic pattern", value: "E-W all-reduce", color: C.muted },
              { label: "Congestion risk", value: "High w/ oversub", color: "#ef4444" },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 10px", flex: 1 }}>
                <div style={{ color, fontSize: 12, fontWeight: 700 }}>{value}</div>
                <div style={{ color: C.muted, fontSize: 10 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom callout */}
      <div style={{ marginTop: 20, background: C.card, border: `1px solid ${C.border}`, borderRadius: 10, padding: "12px 24px", maxWidth: 720, textAlign: "center" }}>
        <p style={{ color: C.text, fontSize: 13, margin: 0, lineHeight: 1.7 }}>
          <strong style={{ color: C.aiPacket }}>All-reduce</strong> during gradient synchronization means every node transmits at the same time.
          Statistical multiplexing <em>breaks down</em>, causing <strong style={{ color: "#ef4444" }}>tail latency spikes</strong> that reduce GPU utilization.
          AI fabrics move toward <strong style={{ color: C.server }}>non-blocking</strong> (1:1 or better) to maintain consistent iteration times.
        </p>
      </div>
    </div>
  );
}
