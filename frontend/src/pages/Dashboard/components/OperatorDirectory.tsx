import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR USER DIRECTORY & MODAL ACTIONS
// =========================================================================
export interface Operator {
  id: string | number;
  identityString: string;
  role: 'Admin' | 'DevSecOps' | 'Operator';
  status: 'Active' | 'Suspended' | 'Idle';
}

interface OperatorDirectoryProps {
  /** Controller flag to show/hide this directory pane based on the navigation state */
  isVisible: boolean;
  /** Complete list of authorized operators retrieved from the backend state */
  operators: Operator[];
  /** Preserved structured localization labels and context mappings */
  translations: {
    hdrDirectoryTitle: string;
    lblTotalUsers: string;
    thDirId: string;
    thDirIdentity: string;
    thDirRole: string;
    thDirStatus: string;
    thDirActions: string;
    btnActionModify: string;
    btnActionSuspend: string;
    modalActionTitle: string;
    modalActionBody: string;
    modalRoleSelectLabel: string;
    btnModalCancel: string;
    btnModalConfirm: string;
  };
  
  // Modal states for administrative actions
  isModalOpen: boolean;
  selectedOperator: Operator | null;
  modalTargetRole: 'Admin' | 'DevSecOps' | 'Operator';
  onOpenModal: (operator: Operator, actionType: 'role' | 'suspend') => void;
  onCloseModal: () => void;
  onTargetRoleChange: (role: 'Admin' | 'DevSecOps' | 'Operator') => void;
  onExecuteAction: () => void;
}

/**
 * OperatorDirectory Component
 * 
 * Manages the layout of active human administrative node connections and handles modal overlays.
 * Fully eliminates legacy Bootstrap dependencies (such as jquery-triggered modals)
 * and replaces them with fully managed React states while preserving exact original IDs.
 */
export const OperatorDirectory: React.FC<OperatorDirectoryProps> = ({
  isVisible,
  operators,
  translations,
  isModalOpen,
  selectedOperator,
  modalTargetRole,
  onOpenModal,
  onCloseModal,
  onTargetRoleChange,
  onExecuteAction,
}) => {
  
  if (!isVisible) return null;

  // Determine styling for user statuses
  const getStatusBadge = (status: Operator['status']) => {
    switch (status) {
      case 'Active':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'Suspended':
        return 'bg-rose-500/10 text-rose-400 border border-rose-500/20 animate-pulse';
      case 'Idle':
      default:
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
    }
  };

  return (
    <div id="directory-pane" className="animate-fadeIn">
      <div className="row">
        <div className="col-12">
          
          {/* Central Directory Container Box */}
          <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:border-white/10 transition-all duration-300">
            
            {/* Header Area with Live Operator Counts */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
              <h4 className="m-0 text-sm font-bold text-white flex items-center gap-2.5" id="hdr-directory-title">
                <i className="fa-solid fa-users-gear text-blue-400"></i>
                {translations.hdrDirectoryTitle}
              </h4>
              <div className="bg-slate-800 border border-white/5 px-4 py-2 rounded-xl text-xs flex items-center gap-2">
                <span id="lbl-total-users" className="text-slate-400 font-medium">
                  {translations.lblTotalUsers}
                </span>:
                <span id="user-count" className="font-extrabold text-white text-sm">
                  {operators.length}
                </span>
              </div>
            </div>

            {/* Operator Listing Table Block */}
            <div className="overflow-x-auto w-full">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-white/5">
                    <th id="th-dir-id" className="text-slate-400 text-[11px] uppercase tracking-wider py-4 font-semibold px-2">
                      {translations.thDirId}
                    </th>
                    <th id="th-dir-identity" className="text-slate-400 text-[11px] uppercase tracking-wider py-4 font-semibold px-2">
                      {translations.thDirIdentity}
                    </th>
                    <th id="th-dir-role" className="text-slate-400 text-[11px] uppercase tracking-wider py-4 font-semibold px-2">
                      {translations.thDirRole}
                    </th>
                    <th id="th-dir-status" className="text-slate-400 text-[11px] uppercase tracking-wider py-4 font-semibold px-2">
                      {translations.thDirStatus}
                    </th>
                    <th id="th-dir-actions" className="text-slate-400 text-[11px] uppercase tracking-wider py-4 font-semibold text-end px-2">
                      {translations.thDirActions}
                    </th>
                  </tr>
                </thead>
                <tbody id="directory-table-body" className="divide-y divide-white/[0.03]">
                  {operators.map((operator) => (
                    <tr key={operator.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-4 px-2 text-sm text-slate-400 font-mono">#{operator.id}</td>
                      <td className="py-4 px-2 text-sm text-slate-200 font-semibold">{operator.identityString}</td>
                      <td className="py-4 px-2 text-sm text-slate-300">
                        <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] font-semibold px-2.5 py-1 rounded-md">
                          {operator.role}
                        </span>
                      </td>
                      <td className="py-4 px-2 text-sm">
                        <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full ${getStatusBadge(operator.status)}`}>
                          {operator.status}
                        </span>
                      </td>
                      <td className="py-4 px-2 text-sm text-end space-x-2">
                        <button
                          type="button"
                          onClick={() => onOpenModal(operator, 'role')}
                          className="bg-white/5 hover:bg-white/10 text-slate-200 border border-white/10 rounded-lg px-3 py-1.5 text-xs font-semibold cursor-pointer transition-all focus:outline-none"
                        >
                          {translations.btnActionModify}
                        </button>
                        <button
                          type="button"
                          onClick={() => onOpenModal(operator, 'suspend')}
                          className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/25 rounded-lg px-3 py-1.5 text-xs font-semibold cursor-pointer transition-all focus:outline-none"
                        >
                          {translations.btnActionSuspend}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>

      {/* Reactive Action Modal Node (Ported cleanly from Bootstrap) */}
      {isModalOpen && (
        <div 
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn"
          role="dialog"
          aria-modal="true"
          id="actionModal"
        >
          <div 
            className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-6 shadow-2xl relative animate-scaleUp"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-4 border-b border-white/5 pb-3">
              <h5 className="text-white font-bold text-base tracking-wide" id="modal-action-title">
                {translations.modalActionTitle}
              </h5>
              <button 
                type="button" 
                onClick={onCloseModal}
                className="text-slate-400 hover:text-white transition-colors cursor-pointer focus:outline-none"
                aria-label="Close"
              >
                <i className="fa-solid fa-xmark text-lg"></i>
              </button>
            </div>

            {/* Modal Body Content */}
            <div className="mb-6">
              <p className="text-slate-400 text-xs leading-relaxed font-medium mb-4 animate-fadeIn" id="modal-action-body">
                {translations.modalActionBody} <strong>{selectedOperator?.identityString}</strong>
              </p>
              
              {/* Dynamic Role Selector Element */}
              <div id="role-select-wrapper" className="space-y-2">
                <label className="block text-xs font-semibold text-slate-400" htmlFor="modal-role-select">
                  {translations.modalRoleSelectLabel}
                </label>
                <select 
                  id="modal-role-select"
                  value={modalTargetRole}
                  onChange={(e) => onTargetRoleChange(e.target.value as Operator['role'])}
                  className="w-full bg-[#0f172a] text-white border border-slate-700 rounded-xl px-3 py-2.5 text-xs focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all cursor-pointer"
                >
                  <option value="Admin">Admin</option>
                  <option value="DevSecOps">DevSecOps</option>
                  <option value="Operator">Operator</option>
                </select>
              </div>
            </div>

            {/* Modal Footer Controls */}
            <div className="flex justify-end gap-3 border-0">
              <button 
                type="button" 
                id="btn-modal-cancel"
                onClick={onCloseModal}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg px-4 py-2 text-xs font-semibold transition-all cursor-pointer focus:outline-none"
              >
                {translations.btnModalCancel}
              </button>
              <button 
                type="button" 
                id="btn-modal-confirm"
                onClick={onExecuteAction}
                className="bg-blue-600 hover:bg-blue-500 text-white rounded-lg px-4 py-2 text-xs font-semibold transition-all cursor-pointer shadow-[0_4px_12px_rgba(59,130,246,0.25)] focus:outline-none"
              >
                {translations.btnModalConfirm}
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};