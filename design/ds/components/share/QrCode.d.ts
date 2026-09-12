/** QR code as inline SVG (ink on white, quiet zone included). Encodes `text` or renders a supplied module matrix. */
export interface QrCodeProps {
  /** Text to encode (byte mode, versions 1–10). */
  text?: string;
  /** Precomputed matrix; overrides `text`. */
  modules?: boolean[][];
  level?: 'L' | 'M';
  /** CSS size; defaults to the qr size token (200px). */
  size?: string | number;
  label?: string;
}
export function QrCode(props: QrCodeProps): JSX.Element | null;
