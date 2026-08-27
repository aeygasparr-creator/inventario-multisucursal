interface StatCardProps {
  label: string;
  value: string | number;
  accent?: "gold" | "red";
}

export default function StatCard({ label, value, accent = "gold" }: StatCardProps) {
  return (
    <div className={`stat-card accent-${accent}`}>
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
    </div>
  );
}
