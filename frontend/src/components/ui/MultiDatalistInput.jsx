import React, { useId, useMemo, useState } from "react";
import { Badge, Button, Form, InputGroup } from "react-bootstrap";

function normalizeValue(value) {
	return String(value || "").trim();
}

export default function MultiDatalistInput({
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
	const inputId = id || `multi-datalist-${autoId}`;
	const listId = `${inputId}-list`;
	const [draft, setDraft] = useState("");

	const normalizedValues = useMemo(() => (values || []).map(normalizeValue).filter(Boolean), [values]);

	const handleAdd = () => {
		const next = normalizeValue(draft);
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
		<Form.Group>
			{label ? <Form.Label className='fw-semibold'>{label}</Form.Label> : null}
			<InputGroup className='flex-wrap gap-2'>
				<Form.Control
					id={inputId}
					list={listId}
					value={draft}
					onChange={(e) => setDraft(e.target.value)}
					placeholder={placeholder}
					required={required && normalizedValues.length === 0}
					disabled={disabled}
					isInvalid={Boolean(error)}
					className='flex-grow-1 min-w-0'
					onKeyDown={(e) => {
						if (e.key === "Enter") {
							e.preventDefault();
							if (canAdd) handleAdd();
						}
					}}
				/>
				<Button
					variant='outline-secondary'
					disabled={disabled || !canAdd}
					onClick={handleAdd}
					className='flex-shrink-0'>
					{addLabel}
				</Button>
			</InputGroup>
			<datalist id={listId}>
				{(options || []).map((opt) => (
					<option key={opt} value={opt} />
				))}
			</datalist>

			{helpText ? <Form.Text className='text-muted d-block mt-1'>{helpText}</Form.Text> : null}
			{error ? (
				<Form.Control.Feedback type='invalid' className='d-block mt-1'>
					{error}
				</Form.Control.Feedback>
			) : null}

			{normalizedValues.length > 0 ? (
				<div className='d-flex flex-wrap gap-2 mt-2 w-100'>
					{normalizedValues.map((v) => (
						<Badge key={v} bg='secondary' className='d-inline-flex align-items-center gap-2 py-2 px-2 mw-100 min-w-0'>
							<span className='text-truncate d-inline-block mw-100 min-w-0'>{v}</span>
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
