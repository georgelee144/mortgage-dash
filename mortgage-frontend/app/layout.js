import "./globals.css";

export const metadata = {
  title: "Mortgage Dashboard",
  description: "Financial tools for home buyers",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
