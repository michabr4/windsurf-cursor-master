export default function WeakAreasPanel({ weakAreas }) {
  return (
    <section className="card">
      <h2>Weak Areas</h2>
      {weakAreas.length === 0 ? (
        <p>No major weak areas detected.</p>
      ) : (
        weakAreas.map((area) => (
          <div key={area.domain} className="subcard">
            <p>
              <strong>{area.domain}</strong> — score {area.weakness_score}
            </p>
            <p>{area.recommendation}</p>
          </div>
        ))
      )}
    </section>
  );
}
