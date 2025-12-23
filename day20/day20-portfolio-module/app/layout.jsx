import '../styles/globals.css';

export const metadata = {
  title: 'Property Portfolio Module',
  description: 'Host portfolio data visualization module for Framer embed',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
