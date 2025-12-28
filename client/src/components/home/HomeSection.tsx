import { ServiceCard } from '../common/ServiceCard';
import type { SectionConfig } from '../../config/homePageServices';

interface HomeSectionProps {
  section: SectionConfig;
}

export function HomeSection({ section }: HomeSectionProps) {
  const cardCount = section.services.length;

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

      <div className={`
        grid gap-6 justify-center
        ${cardCount === 2 
          ? 'grid-cols-1 md:grid-cols-2 max-w-3xl mx-auto' 
          : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
        }
      `}>
        {section.services.map((service) => (
          <div key={service.id} className="w-full max-w-sm mx-auto">
            <ServiceCard service={service} />
          </div>
        ))}
      </div>
    </section>
  );
}
