"use client";
import React, { useRef, useState } from "react";
import { motion } from "framer-motion";

const SENCHI_MAIN = "#240DBF";
const blurb = "Please enter your address to get a risk assessment specific to your location";

type SearchProps = {
  input: string;
  setInput: (input: string) => void;
  setEnterPressed: (enterPressed: boolean) => void;
};

export default function Search({ input, setInput, setEnterPressed }: SearchProps) {
  const [suggestions, setSuggestions] = useState<google.maps.places.AutocompletePrediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [morphed, setMorphed] = useState(false);
  const autocompleteService = useRef<google.maps.places.AutocompleteService | null>(null);

  // Load Google Places API
  React.useEffect(() => {
    if (!window.google) {
      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY}&libraries=places`;
      script.async = true;
      script.onload = () => {
        autocompleteService.current = new window.google.maps.places.AutocompleteService();
      };
      document.body.appendChild(script);
    } else {
      autocompleteService.current = new window.google.maps.places.AutocompleteService();
    }
  }, []);

  // Fetch suggestions
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInput(value);
    if (value && autocompleteService.current) {
      setLoading(true);
      autocompleteService.current.getPlacePredictions(
        { input: value, types: ["address"], componentRestrictions: { country: "ca" } },
        (predictions) => {
          setSuggestions(predictions || []);
          setLoading(false);
        }
      );
    } else {
      setSuggestions([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      setMorphed(true);
      setSuggestions([]);
      setEnterPressed(true);
    }
  };

  return (
    <motion.div
      animate={
        morphed
          ? {
              top: 32,
              left: "50%",
              x: "-50%",
              y: 0,
              position: "fixed",
              width: 400,
              scale: 0.85,
              zIndex: 50,
            }
          : {
              top: "50%",
              left: "50%",
              x: "-50%",
              y: "-50%",
              position: "fixed",
              width: 600,
              scale: 1,
              zIndex: 50,
            }
      }
      transition={{ type: "spring", stiffness: 400, damping: 40 }}
      style={{ maxWidth: "98vw" }}
    >
      {!morphed && (
        <h1 className="text-2xl font-bold text-senchi-main mb-6 text-center">{blurb}</h1>
      )}
      <div style={{ position: "relative" }}>
        <input
          type="text"
          value={input}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Enter your address..."
          style={{
            width: "100%",
            padding: "16px 20px",
            borderRadius: 12,
            border: `2px solid ${SENCHI_MAIN}`,
            outline: "none",
            fontSize: 18,
            boxShadow: "0 2px 12px rgba(36,13,191,0.07)",
            transition: "border 0.2s, box-shadow 0.2s",
            color: "#2B2C30",
            background: "#fff",
          }}
          autoComplete="off"
        />
        {loading && (
          <div
            style={{
              position: "absolute",
              right: 16,
              top: "50%",
              transform: "translateY(-50%)",
              color: SENCHI_MAIN,
              fontWeight: 600,
              fontSize: 16,
            }}
          >
            ...
          </div>
        )}
      </div>
      {suggestions.length > 0 && (
        <div
          style={{
            background: "#fff",
            border: `1px solid ${SENCHI_MAIN}`,
            borderTop: "none",
            borderRadius: "0 0 12px 12px",
            boxShadow: "0 4px 16px rgba(36,13,191,0.08)",
            marginTop: 0,
            zIndex: 10,
            position: "absolute",
            width: "100%",
            maxWidth: "100%",
            minWidth: "100%",
            maxHeight: 220,
            overflowY: "auto",
            top: 120,
          }}
        >
          {suggestions.map((s, i) => (
            <div
              key={s.place_id}
              style={{
                padding: "12px 20px",
                cursor: "pointer",
                borderBottom: i === suggestions.length - 1 ? "none" : "1px solid #F0F0F0",
                color: "#2B2C30",
                fontSize: 16,
                background: "#fff",
                transition: "background 0.15s",
              }}
              onMouseDown={() => {
                setInput(s.description);
                setSuggestions([]);
              }}
              onMouseOver={e => (e.currentTarget.style.background = "#EBE9FC")}
              onMouseOut={e => (e.currentTarget.style.background = "#fff")}
            >
              {s.description}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}