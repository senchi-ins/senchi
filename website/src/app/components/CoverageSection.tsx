"use client";

export default function CoverageSection() {
  const industries = [
    {
      title: "Water & Wastewater Treatment",
      description:
        "Municipal and industrial water purification, pH adjustment, disinfection, and flocculation chemicals.",
      products: [
        "Sodium Hypochlorite",
        "Ferric Chloride",
        "Calcium Chloride",
        "Sulfuric Acid",
        "Sodium Hydroxide",
      ],
    },
    {
      title: "Pulp & Paper Manufacturing",
      description:
        "Bleaching agents, caustic soda for pulping, and specialty chemicals for paper production.",
      products: [
        "Sodium Hydroxide",
        "Hydrogen Peroxide",
        "Sodium Carbonate",
        "Sulfuric Acid",
      ],
    },
    {
      title: "Agriculture & Fertilizers",
      description:
        "Nitrogen, phosphate, and potassium-based compounds for crop nutrition and soil treatment.",
      products: [
        "Ammonium Nitrate",
        "Phosphoric Acid",
        "Potassium Hydroxide",
        "Calcium Chloride",
      ],
    },
    {
      title: "Food & Beverage Processing",
      description:
        "Food-grade acids, sanitizers, and pH regulators for processing and packaging.",
      products: [
        "Citric Acid",
        "Phosphoric Acid",
        "Acetic Acid",
        "Ethanol (Food Grade)",
      ],
    },
    {
      title: "Mining & Mineral Processing",
      description:
        "Flotation reagents, leaching acids, and process chemicals for ore extraction.",
      products: [
        "Sulfuric Acid",
        "Hydrochloric Acid",
        "Sodium Hydroxide",
        "Methanol",
      ],
    },
    {
      title: "Petrochemical & Refining",
      description:
        "Process chemicals, catalysts, and treatment agents for oil and gas operations.",
      products: [
        "Methanol",
        "Sulfuric Acid",
        "Sodium Hydroxide",
        "Hydrochloric Acid",
      ],
    },
  ];

  return (
    <section
      id="industries"
      className="py-12 bg-[#f5f0e8]"
      style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-10">
          <div
            className="inline-block border-2 border-[#8b7635] bg-[#1a3a1a] px-8 py-3"
            style={{ boxShadow: "3px 3px 0px #8b7635" }}
          >
            <h2 className="text-[#d4c9a8] text-xl sm:text-2xl font-bold tracking-wider uppercase">
              Industries We Serve
            </h2>
          </div>
          <p className="mt-4 text-[#1a3a1a] max-w-2xl mx-auto">
            Senchi Chemical provides reliable supply to a wide range of
            industries. Our technical sales staff can recommend the right
            product for your application.
          </p>
        </div>

        {/* Industries grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          {industries.map((industry, i) => (
            <div
              key={i}
              className="border-2 border-[#8b7635] bg-white"
              style={{ boxShadow: "3px 3px 0px #8b7635" }}
            >
              <div className="bg-[#1a3a1a] px-4 py-2 border-b-2 border-[#8b7635]">
                <h3 className="text-[#d4c9a8] font-bold text-sm uppercase tracking-wider">
                  {industry.title}
                </h3>
              </div>
              <div className="p-4">
                <p className="text-sm text-[#1a3a1a] mb-3 leading-relaxed">
                  {industry.description}
                </p>
                <div className="border-t border-[#d4c9a8] pt-3">
                  <div className="text-xs uppercase tracking-wider text-[#8b7635] font-bold mb-2">
                    Key Products:
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {industry.products.map((product, j) => (
                      <span
                        key={j}
                        className="inline-block bg-[#f5f0e8] border border-[#d4c9a8] px-2 py-0.5 text-xs text-[#1a3a1a]"
                      >
                        {product}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* About section */}
        <div
          id="about"
          className="border-2 border-[#8b7635] bg-white"
          style={{ boxShadow: "3px 3px 0px #8b7635" }}
        >
          <div className="bg-[#8b7635] px-6 py-2 border-b-2 border-[#8b7635]">
            <h3 className="text-white font-bold text-sm uppercase tracking-wider text-center">
              About Senchi Chemical Supply Co.
            </h3>
          </div>
          <div className="p-6 sm:p-8">
            <div className="grid md:grid-cols-2 gap-8">
              <div className="space-y-4 text-sm text-[#1a3a1a] leading-relaxed">
                <p>
                  <strong>Senchi Chemical Supply Co.</strong> was founded in
                  1987 in Mississauga, Ontario by industrial chemist Gerald R.
                  Dawes. What began as a small caustic soda reseller has grown
                  into one of Canada&apos;s most trusted commodity chemical
                  manufacturers.
                </p>
                <p>
                  Our 120,000 sq. ft. manufacturing campus houses chlor-alkali
                  cells, acid reactors, distillation columns, and blending
                  facilities capable of producing over 50,000 metric tonnes of
                  product annually.
                </p>
                <p>
                  We source commodity feedstocks&mdash;salt, sulfur, natural
                  gas, corn, phosphate rock, and limestone&mdash;and transform
                  them into the essential chemicals that keep industry running.
                </p>
              </div>
              <div className="space-y-4 text-sm text-[#1a3a1a] leading-relaxed">
                <p>
                  Our commitment to quality is backed by ISO 9001:2015 and ISO
                  14001 certifications. Every batch ships with a Certificate of
                  Analysis. Our laboratory runs 24 hours a day to ensure the
                  purity and consistency our customers depend on.
                </p>
                <p>
                  With a fleet of dedicated tanker trucks and access to CN and
                  CP rail networks, we deliver anywhere in Canada and the
                  continental United States. Emergency and same-day shipments
                  available for select products.
                </p>
                <p className="font-bold text-[#8b7635]">
                  &ldquo;Quality chemicals from commodity roots &mdash;
                  delivered on time, every time.&rdquo;
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
