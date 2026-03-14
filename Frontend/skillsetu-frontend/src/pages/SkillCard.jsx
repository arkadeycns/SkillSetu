export default function SkillCard({ name, onClick }) {
  return (
    <div
      onClick={onClick}
      className="border p-6 rounded-xl shadow hover:shadow-lg cursor-pointer"
    >
      <h2 className="text-xl font-semibold">{name}</h2>
    </div>
  );
}
