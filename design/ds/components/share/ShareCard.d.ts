/**
 * The Share screen card: QR code, data-pack date and size, app size, two buttons and the plain statement of what the app does not claim.
 * @startingPoint section="Screens" subtitle="Share card with QR code" viewport="360x560"
 */
export interface ShareCardProps {
  /** Text the QR code encodes (URL or file handoff) */
  qrText?: string;
  qrModules?: boolean[][];
  /** ISO date of the data pack */
  packDate?: string;
  /** e.g. "212 KB" */
  packSize?: string;
  /** e.g. "810 KB" */
  appSize?: string;
  buildSource?: string;
  onShare?: () => void;
  onSave?: () => void;
  shareLabel?: string;
  saveLabel?: string;
  statement?: string;
}
export function ShareCard(props: ShareCardProps): JSX.Element;
