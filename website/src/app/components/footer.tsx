import React from 'react'
import Image from 'next/image';

import { style } from '../../config'

// Example SVG icons (replace with your own or use a library)
const TwitterIcon = () => (
  <Image src="/icons/twitter.png" alt="Twitter" width={24} height={24} />
);
const InstagramIcon = () => (
  <Image src="/icons/instagram.png" alt="Instagram" width={24} height={24} />
);
const TikTokIcon = () => (
  <Image src="/icons/tiktok.png" alt="TikTok" width={24} height={24} />
);

export type Social = {
  name: string;
  icon: React.ReactNode;
  href: string;
};

export type FooterLink = {
  name: string;
  href: string;
};

export type ContactInfo = {
  phone: string;
  address: string;
  email: string;
};

interface FooterProps {
  socials?: Social[];
  contact?: ContactInfo;
  links?: FooterLink[];
  disclaimer?: string;
}

const defaultSocials: Social[] = [
  { name: 'Twitter', icon: <TwitterIcon />, href: '' },
  { name: 'Instagram', icon: <InstagramIcon />, href: '' },
  { name: 'TikTok', icon: <TikTokIcon />, href: '' }
];

const defaultContact: ContactInfo = {
  phone: '',
  address: '',
  email: 'help@senchi.ca',
};

const defaultLinks: FooterLink[] = [
  // { name: 'Terms of Service', href: '#' },
  // { name: 'Legal', href: '#' },
  // { name: 'Accessibility', href: '#' },
];

const defaultDisclaimer =
  'Disclaimer: Senchi is not yet a licenced insurance provider. We do not offer underwriting or policy services, only the underlying technology to support them.';

export default function Footer({
  socials = defaultSocials,
  contact = defaultContact,
  links = defaultLinks,
  disclaimer = defaultDisclaimer,
}: FooterProps) {
    const proudly_canadian_aspect_ratio = 33 / 173;
    const proudly_canadian_width = 173;
    return (
        <footer className={`w-full ${style.colors.sections.footer.bg} border-t border-gray-300 text-sm`}>
        <div className="w-full max-w-7xl mx-auto px-16 py-8 flex flex-col gap-8">
            <div className="flex flex-col md:flex-row md:justify-between gap-8">
            <div>
                <h2 className="font-bold mb-2">Contact</h2>
                <div>{contact.phone}</div>
                <div>{contact.address}</div>
                <div><a href={`mailto:${contact.email}`} className="underline">{contact.email}</a></div>
                <div className='mt-4'>
                    <Image alt='Proudly Canadian' src="/proudly_canadian.svg" width={proudly_canadian_width} height={proudly_canadian_width * proudly_canadian_aspect_ratio}/>
                </div>
            </div>
            <div>
                <h2 className="font-bold mb-2">Follow us</h2>
                <div className="flex gap-4">
                {socials.map((social) => (
                    <a
                    key={social.name}
                    href={social.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={social.name}
                    className="hover:text-blue-600 transition-colors flex items-center gap-1"
                    >
                    {social.icon}
                    <span className="sr-only">{social.name}</span>
                    </a>
                ))}
                </div>
            </div>
            <div>
                {/* <h2 className="font-bold mb-2">Links</h2>
                <ul>
                {links.map((link) => (
                    <li key={link.name}>
                    <a href={link.href} className="underline hover:text-blue-600 transition-colors">{link.name}</a>
                    </li>
                ))}
                </ul> */}
            </div>
            </div>
            <div className="text-xs text-gray-500 border-t border-gray-200 pt-6">
            {disclaimer}
            </div>
        </div>
        </footer>
    );
}
