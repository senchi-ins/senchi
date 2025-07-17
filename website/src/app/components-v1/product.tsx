import React from 'react'
import { style } from '../../config'

export type ProductCard = {
  icon: React.ReactNode;
  name: string;
  description: string;
  features: string[];
  video?: string;
};

interface ProductProps {
  products?: ProductCard[];
}

export default function Product({ products = [] }: ProductProps) {
  return (
    <section className={`w-full ${style.colors.sections.product.bg} border-t border-gray-300`}>
      <div className="h-[80vh] flex flex-col justify-center max-w-7xl mx-auto px-16 pb-0 mb-0">
      <h1 className={`text-5xl font-bold text-left max-w-[75%] pt-3 ${style.colors.sections.product.mainFont}`}>
            More money for you and your customers
      </h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full h-full items-center">
            {products.map((product, id) => (
              <div key={id}>

              </div>
            ))}
        </div>
      </div>
    </section>
  );
}
