import { useEffect, useState } from "react";

const COLORS = {
  spine: "#6366f1",
  leaf: "#06b6d4",
  tor: "#f59e0b",
  server: "#10b981",
  link: "#475569",
  packet: "#f43f5e",
  bg: "#0f172a",
  card: "#1e293b",
  border: "#334155",
  text: "#f1f5f9",
  muted: "#94a3b8",
};

function Node({ label, sublabel, color, x, y, w = 80, h = 36 }: {
  label: string; sublabel?: string; color: string; x: number; y: number; w?: number; h?: number;
}) {
  return (
    <g>
      <rect x={x - w / 2} y={y - h / 2} width={w} height={h} rx={6}
        fill={color} fillOpacity={0.15} stroke={color} strokeWidth={1.5} />
      <text x={x} y={sublabel ? y - 2 : y + 5} textAnchor="middle"
        fill={COLORS.text} fontSize={11} fontWeight={600}>{label}</text>
      {sublabel && <text x={x} y={y + 11} textAnchor="middle"
        fill={COLORS.muted} fontSize={9}>{sublabel}</text>}
    </g>
  );
}

function Link({ x1, y1, x2, y2, active = false }: {
  x1: number; y1: number; x2: number; y2: number; active?: boolean;
}) {
  return (
    <line x1={x1} y1={y1} x2={x2} y2={y2}
      stroke={active ? COLORS.packet : COLORS.link}
      strokeWidth={active ? 2 : 1.5}
      strokeOpacity={active ? 1 : 0.4}
      strokeDasharray={active ? "none" : "none"} />
  );
}

function AnimatedPacket({ x1, y1, x2, y2, delay, duration = 1.8, visible }: {
  x1: number; y1: number; x2: number; y2: number;
  delay: number; duration?: number; visible: boolean;
}) {
  const [t, setT] = useState(0);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (!visible) return;
    const timeout = setTimeout(() => {
      setActive(true);
      let start: number;
      const animate = (ts: number) => {
        if (!start) start = ts;
        const progress = Math.min((ts - start) / (duration * 1000), 1);
        setT(progress);
        if (progress < 1) requestAnimationFrame(animate);
        else {
          setTimeout(() => {
            setT(0);
            setActive(false);
            setTimeout(() => setActive(true), 200);
          }, 300);
        }
      };
      requestAnimationFrame(animate);
    }, delay * 1000);
    return () => clearTimeout(timeout);
  }, [visible, delay, duration]);

  if (!active) return null;
  const cx = x1 + (x2 - x1) * t;
  const cy = y1 + (y2 - y1) * t;
  return <circle cx={cx} cy={cy} r={5} fill={COLORS.packet} opacity={0.9} />;
}

function TierDiagram({ tier, x, y, animated }: {
  tier: 2 | 3; x: number; y: number; animated: boolean;
}) {
  const spineY = y + 30;
  const leafY = tier === 3 ? y + 130 : y + 130;
  const torY = tier === 3 ? y + 230 : null;
  const serverY = tier === 3 ? y + 330 : y + 230;

  const spines = tier === 2
    ? [x - 100, x, x + 100]
    : [x - 80, x + 80];

  const leaves = tier === 2
    ? [x - 100, x + 100]
    : [x - 80, x + 80];

  const tors = tier === 3 ? [x - 80, x + 80] : [];

  const servers = tier === 2
    ? [x - 130, x - 70, x + 70, x + 130]
    : [x - 130, x - 30, x + 30, x + 130];

  const title = tier === 2 ? "2-Tier Clos" : "3-Tier Clos";
  const desc = tier === 2
    ? "ToR acts as leaf → direct spine connection"
    : "ToR → Leaf → Spine — extra switching stage";

  return (
    <g>
      <text x={x} y={y - 10} textAnchor="middle" fill={COLORS.text}
        fontSize={15} fontWeight={700}>{title}</text>
      <text x={x} y={y + 8} textAnchor="middle" fill={COLORS.muted} fontSize={10}>{desc}</text>

      {/* Spine layer */}
      {spines.map((sx, i) => (
        <Node key={i} label="Spine" sublabel={`S${i + 1}`}
          color={COLORS.spine} x={sx} y={spineY} w={70} h={34} />
      ))}

      {/* Leaf layer */}
      {leaves.map((lx, i) => (
        <Node key={i} label={tier === 2 ? "Leaf/ToR" : "Leaf"}
          sublabel={`L${i + 1}`} color={COLORS.leaf} x={lx} y={leafY} w={72} h={34} />
      ))}

      {/* ToR layer (3-tier only) */}
      {tors.map((tx, i) => (
        <Node key={i} label="ToR" sublabel={`T${i + 1}`}
          color={COLORS.tor} x={tx} y={torY!} w={64} h={32} />
      ))}

      {/* Servers */}
      {servers.map((sx, i) => (
        <Node key={i} label="Server" color={COLORS.server} x={sx} y={serverY} w={62} h={30} />
      ))}

      {/* Spine–Leaf links */}
      {spines.flatMap((sx) =>
        leaves.map((lx, li) => (
          <Link key={`${sx}-${li}`} x1={sx} y1={spineY + 17} x2={lx} y2={leafY - 17} />
        ))
      )}

      {/* Leaf–ToR links (3-tier) */}
      {tier === 3 && leaves.flatMap((lx, li) =>
        [tors[li]].filter(Boolean).map((tx) => (
          <Link key={`l${li}-t`} x1={lx} y1={leafY + 17} x2={tx!} y2={torY! - 16} />
        ))
      )}

      {/* ToR/Leaf–Server links */}
      {tier === 2
        ? leaves.flatMap((lx, li) =>
          [servers[li * 2], servers[li * 2 + 1]].map((sx, si) => (
            <Link key={`${li}-${si}`} x1={lx} y1={leafY + 17} x2={sx} y2={serverY - 15} />
          ))
        )
        : tors.flatMap((tx, ti) =>
          [servers[ti * 2], servers[ti * 2 + 1]].map((sx, si) => (
            <Link key={`${ti}-${si}`} x1={tx} y1={torY! + 16} x2={sx} y2={serverY - 15} />
          ))
        )
      }

      {/* Animated packets (server → spine path) */}
      {animated && (
        <>
          <AnimatedPacket x1={servers[0]} y1={serverY - 15}
            x2={tier === 2 ? leaves[0] : tors[0]}
            y2={tier === 2 ? leafY + 17 : torY! + 16}
            delay={0} visible={animated} />
          <AnimatedPacket
            x1={tier === 2 ? leaves[0] : tors[0]}
            y1={tier === 2 ? leafY - 17 : torY! - 16}
            x2={tier === 2 ? leaves[0] : leaves[0]}
            y2={tier === 2 ? spineY + 17 : leafY + 17}
            delay={0.3} visible={animated} />
          {tier === 3 && (
            <AnimatedPacket x1={leaves[0]} y1={leafY - 17}
              x2={spines[0]} y2={spineY + 17}
              delay={0.6} visible={animated} />
          )}
          <AnimatedPacket x1={servers[3]} y1={serverY - 15}
            x2={tier === 2 ? leaves[1] : tors[1]}
            y2={tier === 2 ? leafY + 17 : torY! + 16}
            delay={0.9} visible={animated} />
        </>
      )}

      {/* Layer labels */}
      <text x={x - 175} y={spineY + 5} fill={COLORS.spine} fontSize={10} fontWeight={600} opacity={0.8}>SPINE</text>
      <text x={x - 175} y={leafY + 5} fill={COLORS.leaf} fontSize={10} fontWeight={600} opacity={0.8}>
        {tier === 2 ? "LEAF/ToR" : "LEAF"}
      </text>
      {tier === 3 && torY && (
        <text x={x - 175} y={torY + 5} fill={COLORS.tor} fontSize={10} fontWeight={600} opacity={0.8}>ToR</text>
      )}
      <text x={x - 175} y={serverY + 5} fill={COLORS.server} fontSize={10} fontWeight={600} opacity={0.8}>SERVERS</text>
    </g>
  );
}

export function TierComparison() {
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 800);
    return () => clearTimeout(t);
  }, []);

  return (
    <div style={{ background: COLORS.bg, minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "24px" }}>
      <h2 style={{ color: COLORS.text, fontSize: 22, fontWeight: 800, marginBottom: 4, textAlign: "center", letterSpacing: "-0.5px" }}>
        Clos Fabric: Tier Architectures
      </h2>
      <p style={{ color: COLORS.muted, fontSize: 13, marginBottom: 24, textAlign: "center" }}>
        Every switching stage counts — 2-tier vs 3-tier changes cost, latency, and scale
      </p>

      <svg width={780} height={420} style={{ overflow: "visible" }}>
        {/* Divider */}
        <line x1={390} y1={20} x2={390} y2={400} stroke={COLORS.border} strokeWidth={1} strokeDasharray="4,4" />

        <TierDiagram tier={2} x={195} y={50} animated={animated} />
        <TierDiagram tier={3} x={585} y={50} animated={animated} />

        {/* Packet legend */}
        <circle cx={660} cy={405} r={5} fill={COLORS.packet} />
        <text x={670} y={409} fill={COLORS.muted} fontSize={11}>Packet in flight</text>
      </svg>

      <div style={{ display: "flex", gap: 24, marginTop: 16, flexWrap: "wrap", justifyContent: "center" }}>
        {[
          { color: COLORS.spine, label: "Spine — top-level aggregation" },
          { color: COLORS.leaf, label: "Leaf — connects to servers or ToR" },
          { color: COLORS.tor, label: "ToR — Top-of-Rack switch" },
          { color: COLORS.server, label: "Server — compute endpoint" },
        ].map(({ color, label }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: color, opacity: 0.8 }} />
            <span style={{ color: COLORS.muted, fontSize: 12 }}>{label}</span>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 20, background: COLORS.card, border: `1px solid ${COLORS.border}`, borderRadius: 8, padding: "12px 20px", maxWidth: 680, textAlign: "center" }}>
        <p style={{ color: COLORS.text, fontSize: 13, margin: 0 }}>
          <strong style={{ color: COLORS.leaf }}>2-tier:</strong> ToR acts as the leaf and connects directly to spines — fewer hops, simpler cabling, works well at moderate scale.
          &nbsp;&nbsp;<strong style={{ color: COLORS.tor }}>3-tier:</strong> Adds a dedicated leaf layer between ToR and spine — enables larger scale at the cost of extra switching latency.
        </p>
      </div>
    </div>
  );
}
