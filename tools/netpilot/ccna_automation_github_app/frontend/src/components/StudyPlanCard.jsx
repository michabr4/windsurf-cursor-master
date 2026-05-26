export default function StudyPlanCard({ plan }) {
  if (!plan) return null;

  return (
    <section className="card">
      <h2>Study Plan</h2>
      <p>{plan.summary}</p>
      {plan.weekly_plan.map((week) => (
        <div key={week.week} className="subcard">
          <strong>Week {week.week}</strong>
          <p>Focus: {week.focus_domains.join(', ')}</p>
          <ul>
            {week.goals.map((goal) => (
              <li key={goal}>{goal}</li>
            ))}
          </ul>
        </div>
      ))}
    </section>
  );
}
