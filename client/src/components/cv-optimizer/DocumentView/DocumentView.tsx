import '../../../styles/cv-optimizer/document-view.css';

interface DocumentViewProps {
  children: React.ReactNode;
}

export default function DocumentView({ children }: DocumentViewProps) {
  return (
    <div className="document-container">
      <div className="document-paper">
        {children}
      </div>
    </div>
  );
}
