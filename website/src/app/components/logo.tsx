import Image from "next/image";

import React from 'react'

type LogoProps = {
    imgPath: string;
    width: number;
    height: number;
}

export default function Logo( { imgPath, width, height }: LogoProps) {
  return (
    <div>
        <Image 
            src={imgPath} 
            alt="Company logo" 
            width={width} 
            height={height}
        />
    </div>
  )
}
