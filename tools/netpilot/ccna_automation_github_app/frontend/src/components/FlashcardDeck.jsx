export default function FlashcardDeck({ cards }) {
  return (
    <section className="card">
      <h2>Flashcards</h2>
      <div className="grid">
        {cards.map((card, idx) => (
          <article key={`${card.question}-${idx}`} className="subcard">
            <p>
              <strong>Q:</strong> {card.question}
            </p>
            <p>
              <strong>A:</strong> {card.answer}
            </p>
            <small>{card.domain}</small>
          </article>
        ))}
      </div>
    </section>
  );
}
