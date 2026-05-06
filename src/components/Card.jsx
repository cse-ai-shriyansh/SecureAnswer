export default function Card({ children, className = '', ...props }) {
  return (
    <div className={`card-base p-6 ${className}`} {...props}>
      {children}
    </div>
  )
}
