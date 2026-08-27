export default function AiCoreIllustration() {
  return (
    <svg
      viewBox="0 0 320 320"
      width="100%"
      height="100%"
      role="img"
      aria-label="Ilustración decorativa de un núcleo de sistema"
    >
      <defs>
        <radialGradient id="coreGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#d4af37" stopOpacity="0.9" />
          <stop offset="60%" stopColor="#d4af37" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#d4af37" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* anillos concéntricos */}
      <circle cx="160" cy="160" r="140" fill="none" stroke="#5c3d1180" strokeWidth="1" />
      <circle cx="160" cy="160" r="110" fill="none" stroke="#5c3d1180" strokeWidth="1" strokeDasharray="4 6" />
      <circle cx="160" cy="160" r="80" fill="none" stroke="#d4af3755" strokeWidth="1" />

      {/* halo del núcleo */}
      <circle cx="160" cy="160" r="70" fill="url(#coreGlow)" />

      {/* núcleo central */}
      <circle cx="160" cy="160" r="14" fill="#d4af37">
        <animate attributeName="r" values="12;16;12" dur="2.4s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="1;0.7;1" dur="2.4s" repeatCount="indefinite" />
      </circle>

      {/* líneas de circuito */}
      <path d="M160 20 V60 M160 260 V300 M20 160 H60 M260 160 H300" stroke="#5c3d1180" strokeWidth="1" />
      <path d="M160 90 L160 130" stroke="#d4af3788" strokeWidth="1.5" />
      <path d="M90 160 L130 160" stroke="#d4af3788" strokeWidth="1.5" />
      <path d="M230 160 L190 160" stroke="#d4af3788" strokeWidth="1.5" />
      <path d="M160 230 L160 190" stroke="#d4af3788" strokeWidth="1.5" />

      {/* nodos */}
      {[
        [160, 60], [160, 260], [60, 160], [260, 160],
        [90, 90], [230, 90], [90, 230], [230, 230],
      ].map(([cx, cy]) => (
        <circle key={`${cx}-${cy}`} cx={cx} cy={cy} r="3" fill="#d4af37" opacity="0.6" />
      ))}

      {/* arco giratorio */}
      <path d="M160 20 A140 140 0 0 1 300 160" fill="none" stroke="#e8384f" strokeWidth="2" strokeLinecap="round">
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 160 160"
          to="360 160 160"
          dur="6s"
          repeatCount="indefinite"
        />
      </path>
    </svg>
  );
}
