"use client";

export default function HaloSection() {
  const chemicals = [
    {
      name: "Sodium Hydroxide (Caustic Soda)",
      cas: "1310-73-2",
      formula: "NaOH",
      grade: "Industrial / Technical",
      source: "Chlor-alkali process (salt)",
      packaging: "Drums, Totes, Bulk",
      msds: true,
    },
    {
      name: "Hydrochloric Acid",
      cas: "7647-01-0",
      formula: "HCl",
      grade: "Industrial / ACS",
      source: "Salt + Sulfuric acid",
      packaging: "Carboys, Drums, Bulk",
      msds: true,
    },
    {
      name: "Sulfuric Acid",
      cas: "7664-93-9",
      formula: "H₂SO₄",
      grade: "Technical / CP",
      source: "Sulfur combustion",
      packaging: "Drums, Totes, Tanker",
      msds: true,
    },
    {
      name: "Ethanol (Denatured)",
      cas: "64-17-5",
      formula: "C₂H₅OH",
      grade: "SDA 40-B",
      source: "Corn / Sugarcane fermentation",
      packaging: "Drums, Totes",
      msds: true,
    },
    {
      name: "Methanol",
      cas: "67-56-1",
      formula: "CH₃OH",
      grade: "Technical / ACS",
      source: "Natural gas reforming",
      packaging: "Drums, Totes, Bulk",
      msds: true,
    },
    {
      name: "Calcium Chloride",
      cas: "10043-52-4",
      formula: "CaCl₂",
      grade: "Industrial / Food",
      source: "Limestone + HCl",
      packaging: "Bags, Drums, Bulk",
      msds: true,
    },
    {
      name: "Sodium Hypochlorite (Bleach)",
      cas: "7681-52-9",
      formula: "NaOCl",
      grade: "12.5% / 15% Trade",
      source: "Chlor-alkali + chlorination",
      packaging: "Carboys, Drums",
      msds: true,
    },
    {
      name: "Phosphoric Acid",
      cas: "7664-38-2",
      formula: "H₃PO₄",
      grade: "Technical / Food",
      source: "Phosphate rock + acid",
      packaging: "Drums, Totes",
      msds: true,
    },
    {
      name: "Ammonium Nitrate",
      cas: "6484-52-2",
      formula: "NH₄NO₃",
      grade: "Agricultural / Technical",
      source: "Ammonia + Nitric acid",
      packaging: "Bags, Super sacks",
      msds: true,
    },
    {
      name: "Potassium Hydroxide (Caustic Potash)",
      cas: "1310-58-3",
      formula: "KOH",
      grade: "Industrial / FCC",
      source: "Electrolysis of KCl",
      packaging: "Drums, Totes",
      msds: true,
    },
    {
      name: "Acetic Acid (Glacial)",
      cas: "64-19-7",
      formula: "CH₃COOH",
      grade: "Technical / USP",
      source: "Methanol carbonylation",
      packaging: "Drums, Totes",
      msds: true,
    },
    {
      name: "Sodium Carbonate (Soda Ash)",
      cas: "497-19-8",
      formula: "Na₂CO₃",
      grade: "Dense / Light",
      source: "Trona ore processing",
      packaging: "Bags, Bulk",
      msds: true,
    },
    {
      name: "Hydrogen Peroxide",
      cas: "7722-84-1",
      formula: "H₂O₂",
      grade: "35% / 50% Technical",
      source: "Anthraquinone process",
      packaging: "Drums, Totes",
      msds: true,
    },
    {
      name: "Ferric Chloride",
      cas: "7705-08-0",
      formula: "FeCl₃",
      grade: "Technical / Water Treatment",
      source: "Iron + HCl / Cl₂",
      packaging: "Drums, Totes, Bulk",
      msds: true,
    },
    {
      name: "Citric Acid",
      cas: "77-92-9",
      formula: "C₆H₈O₇",
      grade: "Anhydrous / Monohydrate",
      source: "Sugar fermentation (Aspergillus)",
      packaging: "Bags, Drums",
      msds: true,
    },
  ];

  return (
    <section
      id="catalog"
      className="py-12 bg-white"
      style={{ fontFamily: "'Georgia', 'Times New Roman', serif" }}
    >
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-8">
          <div
            className="inline-block border-2 border-[#8b7635] bg-[#1a3a1a] px-8 py-3"
            style={{ boxShadow: "3px 3px 0px #8b7635" }}
          >
            <h2 className="text-[#d4c9a8] text-xl sm:text-2xl font-bold tracking-wider uppercase">
              Product Catalog
            </h2>
          </div>
          <p className="mt-4 text-[#1a3a1a] max-w-3xl mx-auto">
            We manufacture and distribute over 200 chemical products derived
            from commodity feedstocks. Below is a selection of our most popular
            items. For a complete listing or custom formulations, please{" "}
            <a
              href="#contact"
              className="text-[#8b7635] underline hover:text-[#1a3a1a]"
            >
              contact our sales team
            </a>
            .
          </p>
        </div>

        {/* Note box */}
        <div className="mb-6 border-2 border-[#8b7635] bg-[#f5f0e8] p-3 text-sm text-center text-[#1a3a1a]">
          <strong>NOTE:</strong> All products available in bulk quantities.
          Minimum order quantities apply. MSDS / SDS sheets available upon
          request or download. All prices FOB our facility in Mississauga, ON.
        </div>

        {/* Product table */}
        <div
          className="overflow-x-auto border-2 border-[#8b7635]"
          style={{ boxShadow: "3px 3px 0px #8b7635" }}
        >
          <table className="oldschool">
            <thead>
              <tr>
                <th>Chemical Name</th>
                <th>CAS No.</th>
                <th>Formula</th>
                <th>Grade(s)</th>
                <th className="hidden md:table-cell">Commodity Source</th>
                <th className="hidden sm:table-cell">Packaging</th>
                <th>MSDS</th>
              </tr>
            </thead>
            <tbody>
              {chemicals.map((chem, i) => (
                <tr key={i}>
                  <td className="font-bold text-[#1a3a1a]">{chem.name}</td>
                  <td
                    className="text-[#8b7635]"
                    style={{
                      fontFamily: "'Courier New', monospace",
                      fontSize: "0.8rem",
                    }}
                  >
                    {chem.cas}
                  </td>
                  <td style={{ fontFamily: "'Courier New', monospace" }}>
                    {chem.formula}
                  </td>
                  <td>{chem.grade}</td>
                  <td className="hidden md:table-cell text-[#555]">
                    {chem.source}
                  </td>
                  <td className="hidden sm:table-cell">{chem.packaging}</td>
                  <td className="text-center">
                    {chem.msds && (
                      <span className="inline-block bg-[#1a3a1a] text-[#d4c9a8] px-2 py-0.5 text-xs cursor-pointer hover:bg-[#2a5a2a]">
                        PDF
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Bottom note */}
        <div className="mt-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <p className="text-xs text-[#8b7635]">
            * Custom blends and concentrations available upon request. Contact
            our technical department.
          </p>
          <a
            href="#contact"
            className="inline-block bg-[#8b7635] text-white px-5 py-2 text-sm uppercase tracking-wider font-bold hover:bg-[#a08940] transition-colors"
            style={{ border: "2px outset #b09950" }}
          >
            Request Bulk Pricing &gt;&gt;
          </a>
        </div>

        <hr className="fancy" />

        {/* Commodity feedstocks explanation */}
        <div className="grid md:grid-cols-2 gap-8 mt-8">
          <div className="bevel-box">
            <h3 className="text-lg font-bold text-[#1a3a1a] mb-3 uppercase tracking-wider border-b-2 border-[#8b7635] pb-2">
              Our Commodity Feedstocks
            </h3>
            <ul className="space-y-2 text-sm text-[#1a3a1a]">
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Rock Salt &amp; Brine</strong> &mdash; Chlor-alkali
                  electrolysis for NaOH, Cl₂, HCl, and bleach
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Sulfur</strong> &mdash; Contact process for sulfuric
                  acid and downstream products
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Natural Gas</strong> &mdash; Steam reforming for
                  methanol, ammonia, and hydrogen
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Corn &amp; Sugarcane</strong> &mdash; Fermentation for
                  ethanol and citric acid
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Phosphate Rock</strong> &mdash; Acid digestion for
                  phosphoric acid and fertilizers
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Limestone</strong> &mdash; Processing for
                  calcium-based chemical products
                </span>
              </li>
            </ul>
          </div>
          <div className="bevel-box">
            <h3 className="text-lg font-bold text-[#1a3a1a] mb-3 uppercase tracking-wider border-b-2 border-[#8b7635] pb-2">
              Why Senchi Chemical?
            </h3>
            <ul className="space-y-2 text-sm text-[#1a3a1a]">
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Vertically Integrated</strong> &mdash; We buy raw
                  commodities and manufacture in-house for cost control
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Quality Assurance</strong> &mdash; Every batch tested
                  with COA provided. ISO 9001 &amp; ISO 14001 certified
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Logistics Network</strong> &mdash; Owned fleet of
                  tanker trucks and rail car access for continent-wide delivery
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Custom Formulations</strong> &mdash; Our chemists can
                  blend to your exact specifications
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Competitive Pricing</strong> &mdash; Volume discounts
                  for contracts over 10,000 kg/month
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-[#8b7635] font-bold">&raquo;</span>
                <span>
                  <strong>Responsible Care&reg;</strong> &mdash; Committed to
                  environmental stewardship and safety
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
