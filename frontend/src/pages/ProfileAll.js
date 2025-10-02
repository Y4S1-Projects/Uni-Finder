import React, { useState, useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';

export default function ProfileAll() {
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const { currentUser } = useSelector((state) => state.user);
  const [orders, setOrders] = useState([]);
  const [orderIdToDelete, setOrderIdToDelete] = useState('');
  const [showModal, setShowModal] = useState(false);
  const componentPDF = useRef();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await fetch(`http://localhost:3000/api/auth/users/items/`);
      if (!response.ok) {
        throw new Error('Failed to fetch orders');
      }
      const data = await response.json();
      setOrders(data);
    } catch (error) {
      console.error('Error fetching orders:', error);
    }
  };

  const handleDeleteOrder = async () => {
    try {
      const res = await fetch(`/api/user/user_delete/${orderIdToDelete}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        console.log('Error deleting order');
      } else {
        setOrders((prevOrders) => prevOrders.filter((order) => order._id !== orderIdToDelete));
      }
      setShowModal(false);
    } catch (error) {
      console.log(error.message);
    }
  };

  return (
    <div className="container mt-4">
 <h2 className="text-center text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-teal-400 bg-white mb-8 shadow-lg">
  <b>All Reviews</b>
</h2>

      <div ref={componentPDF} className="table-responsive">
        {orders.length > 0 ? (
          <table className="table table-striped table-hover shadow-sm rounded border">
            <thead className="table-light">
              <tr>
                <th>Place</th>
                <th>Reviews</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order._id}>
                  <td className="text-dark">{order.place}</td>
                  <td>{order.review}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-center text-muted">You have no orders yet!</p>
        )}
      </div>

      {/* Bootstrap Modal */}
      {showModal && (
        <div className="modal fade show" tabIndex="-1" aria-labelledby="exampleModalLabel" style={{ display: 'block' }} aria-hidden="true">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title text-center text-danger" id="exampleModalLabel">Delete Order</h5>
                <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close" onClick={() => setShowModal(false)}></button>
              </div>
              <div className="modal-body text-center">
                <p>Are you sure you want to delete this order?</p>
              </div>
              <div className="modal-footer justify-content-center">
                <button 
                  className="btn btn-danger"
                  onClick={handleDeleteOrder}>
                  Yes, I’m sure
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}>
                  No, cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
