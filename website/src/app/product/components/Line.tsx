interface LineProps {
  thickness?: number;
  color?: string;
  className?: string;
}

export function Line({ thickness = 1, color = "#e5e7eb", className = "" }: LineProps) {
  return (
    <div
      className={`w-screen ${className}`}
      style={{
        height: `${thickness}px`,
        backgroundColor: color,
        marginLeft: '0',
        marginRight: 'calc(-50vw + 50%)',
      }}
    />
  );
}
