export function SectionCards() {
  const cardData = [
    {
      id: 1,
      title: "Total Savings",
      value: "$47,012",
    },
    {
      id: 2,
      title: "Claims Avoided",
      value: "$40,012",
    },
    {
      id: 3,
      title: "Premium Savings",
      value: "$7,000",
    },
  ];

  return (
    <div className="flex gap-10 p-6">
      {cardData.map((card) => (
        <div key={card.id}>
          <div className="text-sm text-gray-600 mb-2">{card.title}</div>
          <div className="text-5xl font-bold text-gray-900">{card.value}</div>
        </div>
      ))}
    </div>
  )
}
