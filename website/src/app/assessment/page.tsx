"use client"

import React, { useState, useEffect } from 'react'
import Header from '../components/header'
import { style } from '@/config'
import Search from './search'
import BespokeHouse from '../generated/bespokeHouse'

import { generate_model, test_api } from '@/utils/api'

const url = "https://tripo-data.rg1.data.tripo3d.com/tcli_452312b4252d418cbd41cff1e5c98d35/20250618/21a6930a-143f-44c3-9e2f-db343792298c/tripo_pbr_model_21a6930a-143f-44c3-9e2f-db343792298c.glb?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly90cmlwby1kYXRhLnJnMS5kYXRhLnRyaXBvM2QuY29tL3RjbGlfNDUyMzEyYjQyNTJkNDE4Y2JkNDFjZmYxZTVjOThkMzUvMjAyNTA2MTgvMjFhNjkzMGEtMTQzZi00NGMzLTllMmYtZGIzNDM3OTIyOThjL3RyaXBvX3Bicl9tb2RlbF8yMWE2OTMwYS0xNDNmLTQ0YzMtOWUyZi1kYjM0Mzc5MjI5OGMuZ2xiIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzUwMjkxMjAwfX19XX0_&Signature=iWrhXBjsfvFwt~~ZXi3U3SuR1kcUdVUBXBofBYJvzfcJcKMfwylRj1Iefok9tsrNUABSVAeHms5LCGJICFG62p8E3jloxR-fviw6gt09yKIv56nJ803dDOSF1lUht5UWrez1MOHKqLkbNadLN1~xhROYQMlFKU9~z9t8YwhquD8O7seI8Umn31sPXcPS~OW3E~UdpcqvunMSoUlR5c2HLhTDtWpGhzYAcwOhHQuw9OhC~w4WRzKHkWIGib8VkbdV1G1-RGDcYt-NtXhSUX6tdncG9zaXkpu-k0zHJkW8buqN5dbUbj9qOdo-nJ9Fa9WulG7yT-LD96nIue97oivORQ__&Key-Pair-Id=K1676C64NMVM2J"

export default function Assessment() {
  const [input, setInput] = useState("");
  const [imageURL, setImageURL] = useState(url);
  const [loading, setLoading] = useState(false);
  const [enterPressed, setEnterPressed] = useState(false);

  const handleSearch = async () => {
    const test_response = await test_api();
    console.log(test_response);

    // Load the image into openAI and generate a model
    const image_response = await generate_model(input);
    setImageURL(image_response.image_url);
  };

  useEffect(() => {
    handleSearch();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
    }, 400);
  }, [enterPressed]);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className={`${style.colors.sections.main.bg} flex-1 flex items-center justify-center`}>
        {!enterPressed ? (
          <Search setInput={setInput} input={input} setEnterPressed={setEnterPressed} />
        ) : (
          loading ? (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: 80 }}>
              <svg
                width="48"
                height="48"
                viewBox="0 0 48 48"
                fill="none"
                style={{ display: "block" }}
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="#EBE9FC"
                  strokeWidth="6"
                  fill="none"
                />
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="#240DBF"
                  strokeWidth="6"
                  strokeLinecap="round"
                  fill="none"
                  strokeDasharray="100"
                  strokeDashoffset="60"
                >
                  <animateTransform
                    attributeName="transform"
                    type="rotate"
                    from="0 24 24"
                    to="360 24 24"
                    dur="1s"
                    repeatCount="indefinite"
                  />
                </circle>
              </svg>
            </div>
          ) : (
            <BespokeHouse imageURL={imageURL} />
          )
        )}
      </div>
    </div>
  )
}
