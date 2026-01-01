import DocumentView from '../../components/cv-optimizer/DocumentView';

export default function ResultsPage() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAF9F7' }}>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6" style={{ color: '#1E3A5F' }}>
          CV Analysis Results
        </h1>
        
        <DocumentView>
          CV Document will render here
        </DocumentView>
      </div>
    </div>
  );
}
