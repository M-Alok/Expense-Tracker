import { X, Download } from 'lucide-react';

export default function PdfOptions({ isOpen, onClose, onDownload }) {
  if (!isOpen) return null;

  const periods = [
    { key: 'weekly', label: 'Last 7 Days', description: 'Rolling weekly report' },
    { key: 'current_week', label: 'Current Week', description: 'Monday to today' },
    { key: 'monthly', label: 'Last 30 Days', description: 'Rolling monthly report' },
    { key: 'current_month', label: 'Current Month', description: '1st to today' },
    { key: 'yearly', label: 'Last Year', description: 'Last 365 days' }
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-2xl font-bold text-gray-800">Select Report Period</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="space-y-3">
          {periods.map((period) => (
            <button
              key={period.key}
              onClick={() => onDownload(period.key)}
              className={`w-full flex items-center justify-between px-6 py-4 bg-gray-50 border-2 border-gray-200 rounded-lg hover:bg-gray-100 hover:border-gray-300 transition group`}
            >
              <div className="text-left">
                <p className={`font-semibold text-gray-800`}>
                  {period.label}
                </p>
                <p className="text-sm text-gray-600">{period.description}</p>
              </div>
              <Download className={`w-5 h-5 text-gray-400`} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}