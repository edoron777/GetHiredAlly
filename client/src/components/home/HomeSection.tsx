import { ServiceCard } from '../common/ServiceCard';
import type { SectionConfig } from '../../config/homePageServices';

interface HomeSectionProps {
  section: SectionConfig;
}

export function HomeSection({ section }: HomeSectionProps) {
  return (
    <section className="mb-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-2" style={{ color: '#1E3A5F' }}>
          {section.title}
        </h2>
        <p className="text-gray-600">
          {section.subtitle}
        </p>
      </div>

      <div className={`grid gap-6 ${
        section.services.length === 2 
          ? 'grid-cols-1 md:grid-cols-2' 
          : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
      }`}>
        {section.services.map((service) => (
          <ServiceCard key={service.id} service={service} />
        ))}
      </div>
    </section>
  );
}
