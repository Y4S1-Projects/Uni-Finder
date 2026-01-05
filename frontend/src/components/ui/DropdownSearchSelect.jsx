import React, { useId, useMemo, useRef, useState } from "react";
import { Form, ListGroup } from "react-bootstrap";

export default function DropdownSearchSelect({
	label,
	value,
	onChange,
	options,
	placeholder,
	required,
	disabled,
	error,
	helpText,
	id,
	allowCustom = true,
}) {
	const autoId = useId();
	const inputId = id || `dropdown-search-${autoId}`;
	const containerRef = useRef(null);
	const [open, setOpen] = useState(false);

	const filteredOptions = useMemo(() => {
		const q = String(value || "")
			.trim()
			.toLowerCase();
		const all = Array.isArray(options) ? options : [];
		if (!q) return all;
		return all.filter((opt) => String(opt).toLowerCase().includes(q));
	}, [options, value]);

	return (
		<Form.Group ref={containerRef} className='position-relative'>
			{label ? <Form.Label className='fw-semibold'>{label}</Form.Label> : null}
			<Form.Control
				id={inputId}
				value={value}
				onChange={(e) => {
					if (!allowCustom) {
						// If custom values are not allowed, keep typing but only accept when it matches.
						// For now we still allow typing so filtering works.
					}
					onChange(e.target.value);
				}}
				onFocus={() => setOpen(true)}
				onBlur={() => {
					// Defer close to allow option click.
					setTimeout(() => setOpen(false), 120);
				}}
				placeholder={placeholder}
				required={required}
				disabled={disabled}
				isInvalid={Boolean(error)}
				autoComplete='off'
			/>
			{helpText ? <Form.Text className='text-muted d-block mt-1'>{helpText}</Form.Text> : null}
			{error ? (
				<Form.Control.Feedback type='invalid' className='d-block mt-1'>
					{error}
				</Form.Control.Feedback>
			) : null}

			{open && !disabled ? (
				<div className='position-absolute start-0 end-0 mt-1 border rounded bg-white shadow-sm' style={{ zIndex: 20 }}>
					<ListGroup variant='flush' style={{ maxHeight: 240, overflowY: "auto" }}>
						{filteredOptions.length > 0 ? (
							filteredOptions.map((opt) => (
								<ListGroup.Item
									key={opt}
									action
									onMouseDown={(e) => e.preventDefault()}
									onClick={() => {
										onChange(String(opt));
										setOpen(false);
									}}>
									{opt}
								</ListGroup.Item>
							))
						) : (
							<ListGroup.Item className='text-muted'>No matches</ListGroup.Item>
						)}
					</ListGroup>
				</div>
			) : null}
		</Form.Group>
	);
}
