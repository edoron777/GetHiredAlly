export function SectionSeparator() {
  return (
    <div className="my-12 flex justify-center">
      <div 
        className="w-4/5 h-0.5"
        style={{
          background: 'linear-gradient(90deg, transparent 0%, #1E3A5F 20%, #1E3A5F 80%, transparent 100%)'
        }}
      />
    </div>
  );
}
