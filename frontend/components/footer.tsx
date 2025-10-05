export function Footer() {
  return (
    <footer className="bg-black text-white py-6">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex flex-col md:flex-row justify-between items-center">
         <img
            src="/serplogo.svg"
            alt="Serpentine Logo"
            width={256}
          />
          <div className="flex space-x-4 mt-4 md:mt-0">
          <p className="text-sm">
            © {new Date().getFullYear()} AI Slop. All rights reserved.
          </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
