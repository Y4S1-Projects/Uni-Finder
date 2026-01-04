import React, { useId, useMemo, useState } from "react";
import { Badge, Button, Form, InputGroup, ListGroup } from "react-bootstrap";

function normalizeValue(value) {
	return String(value || "").trim();
}

export default function MultiSelectDropdown({
	label,
	values,
	onChange,
	options,
	placeholder,
	required,
	disabled,
	error,
	helpText,
	id,
	addLabel = "Add",
}) {
	const autoId = useId();
	const inputId = id || `multi-select-${autoId}`;
	const [draft, setDraft] = useState("");
	const [open, setOpen] = useState(false);

	const normalizedValues = useMemo(() => (values || []).map(normalizeValue).filter(Boolean), [values]);

	const availableOptions = useMemo(() => {
		const all = Array.isArray(options) ? options : [];
		const selected = new Set(normalizedValues.map((v) => v.toLowerCase()));
		return all.filter((opt) => !selected.has(String(opt).toLowerCase()));
	}, [normalizedValues, options]);

	const filteredOptions = useMemo(() => {
		const q = normalizeValue(draft).toLowerCase();
		if (!q) return availableOptions;
		return availableOptions.filter((opt) => String(opt).toLowerCase().includes(q));
	}, [availableOptions, draft]);

	const handleAddValue = (valueToAdd) => {
		const next = normalizeValue(valueToAdd);
		if (!next) return;
		if (normalizedValues.some((v) => v.toLowerCase() === next.toLowerCase())) {
			setDraft("");
			return;
		}
		onChange([...normalizedValues, next]);
		setDraft("");
	};

	const handleRemove = (valueToRemove) => {
		onChange(normalizedValues.filter((v) => v !== valueToRemove));
	};

	const canAdd = normalizeValue(draft).length > 0;

	return (
		<Form.Group className='position-relative'>
			{label ? <Form.Label className='fw-semibold'>{label}</Form.Label> : null}

			<InputGroup className='flex-wrap gap-2'>
				<Form.Control
					id={inputId}
					value={draft}
					onChange={(e) => setDraft(e.target.value)}
					onFocus={() => setOpen(true)}
					onBlur={() => setTimeout(() => setOpen(false), 120)}
					placeholder={placeholder}
					required={required && normalizedValues.length === 0}
					disabled={disabled}
					isInvalid={Boolean(error)}
					className='min-w-0 flex-grow-1'
					autoComplete='off'
					onKeyDown={(e) => {
						if (e.key === "Enter") {
							e.preventDefault();
							if (canAdd) handleAddValue(draft);
						}
					}}
				/>
				<Button
					variant='outline-secondary'
					disabled={disabled || !canAdd}
					onClick={() => handleAddValue(draft)}
					className='flex-shrink-0'>
					{addLabel}
				</Button>
			</InputGroup>

			{helpText ? <Form.Text className='mt-1 text-muted d-block'>{helpText}</Form.Text> : null}
			{error ? (
				<Form.Control.Feedback type='invalid' className='mt-1 d-block'>
					{error}
				</Form.Control.Feedback>
			) : null}

			{open && !disabled ? (
				<div className='mt-1 bg-white border rounded shadow-sm position-absolute start-0 end-0' style={{ zIndex: 20 }}>
					<ListGroup variant='flush' style={{ maxHeight: 240, overflowY: "auto" }}>
						{filteredOptions.length > 0 ? (
							filteredOptions.map((opt) => (
								<ListGroup.Item
									key={opt}
									action
									onMouseDown={(e) => e.preventDefault()}
									onClick={() => {
										handleAddValue(opt);
										setOpen(true);
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

			{normalizedValues.length > 0 ? (
				<div className='flex-wrap gap-2 mt-2 d-flex w-100'>
					{normalizedValues.map((v) => (
						<Badge
							key={v}
							bg='secondary'
							pill
							className='min-w-0 gap-2 px-3 py-2 d-inline-flex align-items-center mw-100'>
							<span className='min-w-0 text-truncate d-inline-block mw-100'>{v}</span>
							<Button
								variant='link'
								size='sm'
								className='p-0 text-white text-decoration-none'
								onClick={() => handleRemove(v)}
								disabled={disabled}
								aria-label={`Remove ${v}`}>
								×
							</Button>
						</Badge>
					))}
				</div>
			) : null}
		</Form.Group>
	);
}
